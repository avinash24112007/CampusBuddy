from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from database import Base, engine
from models import caffenity_models, credentials_models, arena_models, problem_box_models, eShoppers_models





@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None,None]:
    print("Starting server lifespan")
    print("Creating new added tables")
    
    Base.metadata.create_all(engine)

    yield

    print("Stopping lifespan event")


app = FastAPI(title="Campus Buddy", lifespan=lifespan)

