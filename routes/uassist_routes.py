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
