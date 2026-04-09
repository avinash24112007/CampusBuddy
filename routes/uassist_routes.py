from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from utils.session_maker import make_db_session
from tools.caffenity import make_caffenity_tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import os

router = APIRouter(prefix="/uassist", tags=["UAssist"])

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    session_id: str

SYSTEM_PROMPT = """You are UAssist, the AI assistant inside the CampusBuddy student super-app.
Your primary role right now is helping students discover food available in campus canteens.
When a student asks you a question, use your tools to query the database.
Be concise, friendly, and helpful. Format your responses nicely in Markdown.
"""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_uassist(request: ChatRequest, db: Session = Depends(make_db_session)):
    # 1. Initialize large language model (requires GROQ_API_KEY in env)
    if os.environ.get('GROQ_API_KEY') is not None:
        api = os.environ.get('GROQ_API_KEY')
    else: 
        print("No API Key Provided")
    
    llm = ChatGroq(
        api_key=api,
        model="llama3-8b-8192", 
        temperature=0.0
    )

    # 2. Create tools using the dynamically injected session
    tools = [make_caffenity_tool(db)]

    # 3. Create the agent using langgraph
    agent_executor = create_react_agent(llm, tools=tools, state_modifier=SYSTEM_PROMPT)

    # 4. Invoke the executor
    try:
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})
        reply = response["messages"][-1].content
    except Exception as e:
        reply = f"Error processing request: {str(e)}"

    return ChatResponse(reply=reply, session_id=request.session_id)


from schemas.uassist_schemas import ArenaChatRequest
from tools.arena import make_arena_tools

ARENA_SYSTEM_PROMPT = """You are UAssist, the AI assistant inside the CampusBuddy student super-app.
You help students discover events, check their registrations, find teammates, and get event details from the Arena module.
Be friendly, concise, and campus-aware.
IMPORTANT Rules:
- If an event is full (0 spots left or filled capacity >= total capacity), proactively mention it.
- If the deadline has passed, explicitly mention that registration is closed.
Format your responses nicely in Markdown.
"""

@router.post("/arena", response_model=ChatResponse)
async def arena_chat_with_uassist(request: ArenaChatRequest, db: Session = Depends(make_db_session)):
    if os.environ.get('GROQ_API_KEY') is not None:
        api = os.environ.get('GROQ_API_KEY')
    else: 
        print("No API Key Provided")
    
    llm = ChatGroq(
        api_key=api,
        model="llama3-8b-8192", 
        temperature=0.0
    )

    tools = make_arena_tools(db)
    
    # Inject user_id directly into the system prompt context so the LLM doesn't have to guess or ask
    dynamic_prompt = ARENA_SYSTEM_PROMPT + f"\n\nCURRENT LOGGED-IN STUDENT ID: {request.user_id}\nAutomatically use this user_id whenever a tool requires it (e.g. check_my_registrations or find_teammates). Do NOT ask the student for their ID."
    
    agent_executor = create_react_agent(llm, tools=tools, state_modifier=dynamic_prompt)

    try:
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})
        reply = response["messages"][-1].content
    except Exception as e:
        reply = f"Error processing request: {str(e)}"

    return ChatResponse(reply=reply, session_id=request.session_id)
