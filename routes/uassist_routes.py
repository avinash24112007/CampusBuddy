from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from utils.session_maker import make_db_session
from tools.caffenity import make_caffenity_tool
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
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

    # 3. Setup Prompt with required placeholders for Tool Calling Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 4. Bind tools and create executor
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 5. Invoke the executor
    try:
        response = agent_executor.invoke({"input": request.message})
        reply = response.get("output", "I had trouble processing that request.")
    except Exception as e:
        reply = f"Error processing request: {str(e)}"

    return ChatResponse(reply=reply, session_id=request.session_id)
