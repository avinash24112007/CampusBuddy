from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from database import Base, engine
from models import caffenity_models, credentials_models, arena_models, problembox_models, user_models, shopperz_models
from routes import uassist_routes, auth_routes, caffenity_routes, shopperz_routes, problembox_routes, user_routes, arena_routes





@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None,None]:
    print("Starting server lifespan")
    print("Creating new added tables")
    
    Base.metadata.create_all(engine)

    yield

    print("Stopping lifespan event")


app = FastAPI(title="Campus Buddy", lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(uassist_routes.router)
app.include_router(caffenity_routes.router)
app.include_router(shopperz_routes.router)
app.include_router(problembox_routes.router)
app.include_router(user_routes.router)
app.include_router(arena_routes.router)


@app.get('/')
def greet():
    return {"message": "Welcome to Campus Buddy"}
