import logging
from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from utils.session_maker import make_db_session
from tools.caffenity import make_caffenity_tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
import inspect
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from tools.arena import make_arena_tools
from tools.shopperz import make_shopperz_tools
from tools.problembox import make_problembox_tools
from tools.map import make_map_tools
from utils.llm_utils import create_agent_fn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uassist", tags=["UAssist"])


class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    type: str = "text"  # "text", "food_cards", "event_cards", "stationery_cards"
    data: list = []


# Structured output target for the agent's final message.
# Using Literal instead of prose instructions makes invalid `type` values
# structurally impossible rather than just discouraged by the prompt.
class UAssistReply(BaseModel):
    message: str = Field(description="Friendly text reply to show the student")
    type: Literal["food_cards", "event_cards", "product_cards", "REPORT", "NAVIGATE", "text"] = Field(
        default="text", description="Use 'text' if no items/actions are being shown"
    )
    data: list = Field(default_factory=list, description="Relevant items found by tools, empty if type is text")


SYSTEM_PROMPT = """You are UAssist, the student super-app AI at KU.
You help students with Food (Caffenity), Events (Arena), Shopping (Shopperz), Reporting (ProblemBox), and Navigation (Map).

- Use 'food_cards' for canteen items.
- Use 'event_cards' for arena events.
- Use 'product_cards' for store products or market listings.
- Use 'REPORT' when a student raises a ticket (include ticket object in data).
- Use 'NAVIGATE' for building/room locations (include location object in data).
- If no items/actions are being shown, use type 'text' and an empty data list.

Be concise and friendly.
"""


def normalize_content(content) -> str:
    """
    LangChain message .content can be a plain string OR a list of content
    blocks (e.g. Gemini returns [{"type": "text", "text": "..."}]).
    This normalizes either shape into a plain string.
    """
    if isinstance(content, list):
        if not content:
            return ""
        item = content[0]
        if isinstance(item, dict):
            return item.get("text", "")
        return str(item)
    return str(content) if content is not None else ""

def domain_tools(request: ChatRequest, db: Session):
    caffenity_tool_agent = create_agent_fn(make_caffenity_tool())
    arena_tool_agent = create_agent_fn(make_arena_tools(db))
    shopperz_tool_agent = create_agent_fn(make_shopperz_tools(db))
    problembox_tool_agent = create_agent_fn(make_problembox_tools(db, request.user_id or "unknown"))
    map_tool_agent = create_agent_fn(make_map_tools(db))
    # Combine all tools for a unified experience
    
    
    @tool
    def _call_caffenity_tool(query: str):
        """
        Call this tool when the user asks querries related to caffetaria/caffenity 

        Args:
            query: Give the tool proper attributes like the food item, user preferences , price, etc from the user query in string format.
        """
        res = caffenity_tool_agent.invoke({
            "messages":[
                SystemMessage(content="You are being called by a supervisor agent on behalf of a student. Treat the following as the student's intent, already extracted."),
                HumanMessage(content=query)
            ]
        })

        return res["messages"][-1].content
    
    return _call_caffenity_tool


@router.post("/chat", response_model=ChatResponse)
async def chat_with_uassist(request: ChatRequest, db: Session = Depends(make_db_session)):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return ChatResponse(message="AI Service Unavailable (Missing Key)", type="text")

    llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-3.1-flash-lite", temperature=0.1, max_retries=3,)

    

    tools = [domain_tools(request, db)]
    

    # Dynamic context (User ID)
    dynamic_prompt = SYSTEM_PROMPT + f"\n\nCONTEXT: Logged-in Student ID: {request.user_id or 'unknown'}"

    # Create the agent with resilient parameter passing across langchain versions.
    sig = inspect.signature(create_agent)
    agent_kwargs = {}
    if "system_prompt" in sig.parameters:
        agent_kwargs["system_prompt"] = dynamic_prompt
    elif "state_modifier" in sig.parameters:
        agent_kwargs["state_modifier"] = dynamic_prompt
    elif "messages_modifier" in sig.parameters:
        agent_kwargs["messages_modifier"] = dynamic_prompt
    elif "system_message" in sig.parameters:
        agent_kwargs["system_message"] = dynamic_prompt

    # response_format makes the agent's own final message structured output
    # directly (single call) instead of needing a second formatting call.
    if "response_format" in sig.parameters:
        agent_kwargs["response_format"] = UAssistReply

    agent_executor = create_agent(llm, tools=tools, **agent_kwargs)

    try:
        response = None
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=request.message)]},
            stream_mode="values"   # <-- "values" gives you the FULL accumulated state each step, not a diff
        ):
            response = chunk  # keep overwriting -- last chunk = final complete state

        # Log what happened, from the final accumulated message list
        for msg in response["messages"]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for call in msg.tool_calls:
                    print(f"[TOOL CALL] {call['name']}  args={call['args']}")
            elif isinstance(msg, ToolMessage):
                print(f"[TOOL RESULT] {msg.name}: {msg.content}")

        structured = response.get("structured_response")
        if structured is not None:
            if isinstance(structured, UAssistReply):
                return ChatResponse(**structured.model_dump())
            if isinstance(structured, dict):
                return ChatResponse(**structured)

        raw_reply = normalize_content(response["messages"][-1].content)
        return ChatResponse(message=raw_reply, type="text")

    except Exception as e:
        logger.exception("uassist chat failed")
        return ChatResponse(message="Sorry, something went wrong. Please try again.", type="text")