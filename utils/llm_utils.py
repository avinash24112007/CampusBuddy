from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
load_dotenv()

def create_agent_fn(tools: list):
    model = "gemini-3.1-flash-lite"
    
    llm = ChatGoogleGenerativeAI(model=model, max_retries=3,)
    agent = create_agent(model= llm , tools=tools)
    return agent


