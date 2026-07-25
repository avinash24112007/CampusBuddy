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
from langchain.agents import create_agent
from tools.arena import make_arena_tools
from tools.shopperz import make_shopperz_tools
from tools.problembox import make_problembox_tools
from tools.map import make_map_tools

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


@router.post("/chat", response_model=ChatResponse)
async def chat_with_uassist(request: ChatRequest, db: Session = Depends(make_db_session)):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return ChatResponse(message="AI Service Unavailable (Missing Key)", type="text")

    llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-3.1-flash-lite", temperature=0.1)

    # Combine all tools for a unified experience
    tools = []
    tools.append(make_caffenity_tool(db))
    tools.extend(make_arena_tools(db))
    tools.extend(make_shopperz_tools(db))
    tools.extend(make_problembox_tools(db, request.user_id or "unknown"))
    tools.extend(make_map_tools(db))

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
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})

        # If response_format was supported, the structured object is typically
        # available under a dedicated key (commonly "structured_response").
        # Confirmed via: print(response.keys()) against your langchain version.
        structured = response.get("structured_response")
        if structured is not None:
            if isinstance(structured, UAssistReply):
                return ChatResponse(**structured.model_dump())
            if isinstance(structured, dict):
                return ChatResponse(**structured)

        # Fallback: response_format wasn't applied (older langchain version, or
        # the key differs) -- degrade gracefully to plain text instead of crashing.
        raw_reply = normalize_content(response["messages"][-1].content)
        return ChatResponse(message=raw_reply, type="text")

    except Exception as e:
        logger.exception("uassist chat failed")
        return ChatResponse(message="Sorry, something went wrong. Please try again.", type="text")