from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from utils.session_maker import make_db_session
from tools.caffenity import make_caffenity_tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import os
from langchain.agents import create_agent
from tools.arena import make_arena_tools
from tools.shopperz import make_shopperz_tools
from tools.problembox import make_problembox_tools
from tools.map import make_map_tools

router = APIRouter(prefix="/uassist", tags=["UAssist"])

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str | None = None

class ChatResponse(BaseModel):
    message: str
    type: str = "text" # "text", "food_cards", "event_cards", "stationery_cards"
    data: list = []

SYSTEM_PROMPT = """You are UAssist, the student super-app AI at KU.
You help students with Food (Caffenity), Events (Arena), Shopping (Shopperz), Reporting (ProblemBox), and Navigation (Map).

STRICT OUTPUT FORMAT:
If you are recommending items, reporting status, or giving directions, you MUST format your final response as a JSON object:
{
  "message": "Your friendly text reply here...",
  "type": "food_cards" | "event_cards" | "product_cards" | "REPORT" | "NAVIGATE" | "text",
  "data": [ ... list of relevant database objects or metadata found by tools ...]
}

- Use 'food_cards' for canteen items.
- Use 'event_cards' for arena events.
- Use 'product_cards' for store products or market listings.
- Use 'REPORT' when a student raises a ticket (include ticket object in data).
- Use 'NAVIGATE' for building/room locations (include location object in data).
- If no items/actions are being shown, use type 'text' and an empty data list.

Be concise and friendly.
"""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_uassist(request: ChatRequest, db: Session = Depends(make_db_session)):
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return ChatResponse(message="AI Service Unavailable (Missing Key)", type="text")
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

    # 2. Combine all tools for a unified experience
    tools = []
    tools.append(make_caffenity_tool(db))
    tools.extend(make_arena_tools(db))
    tools.extend(make_shopperz_tools(db))
    tools.extend(make_problembox_tools(db, request.user_id or "unknown"))
    tools.extend(make_map_tools(db))

    # 3. Dynamic context (User ID)
    dynamic_prompt = SYSTEM_PROMPT + f"\n\nCONTEXT: Logged-in Student ID: {request.user_id or 'unknown'}"

    # 4. Create the agent with resilient parameter passing
    import inspect
    sig = inspect.signature(create_agent)
    agent_kwargs = {}
    if 'state_modifier' in sig.parameters:
        agent_kwargs['state_modifier'] = dynamic_prompt
    elif 'messages_modifier' in sig.parameters:
        agent_kwargs['messages_modifier'] = dynamic_prompt
    elif 'system_message' in sig.parameters:
        agent_kwargs['system_message'] = dynamic_prompt

    agent_executor = create_agent(llm, tools=tools, **agent_kwargs)

    try:
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})
        raw_reply = response["messages"][-1].content
        
        # Try to parse JSON from the LLM response
        import json
        import re
        
        # Look for JSON structure in the reply
        json_match = re.search(r'\{.*\}', raw_reply, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return ChatResponse(
                    message=data.get("message", ""),
                    type=data.get("type", "text"),
                    data=data.get("data", [])
                )
            except:
                pass
        
        return ChatResponse(message=raw_reply, type="text")
        
    except Exception as e:
        return ChatResponse(message=f"Error: {str(e)}", type="text")
