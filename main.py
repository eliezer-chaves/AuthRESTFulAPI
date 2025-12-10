from fastapi import FastAPI
from routers import users, auth
from logging_config import logger
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    #logger.info("Aplication started")
    
    yield
    #logger.info("Aplication ended")


app = FastAPI(
    title="BaseAPI",
    description="API RESTful com autenticação JWT",
    version="1.0.0",
    lifespan=lifespan
)


origins = os.getenv("CORS_ORIGINS")
origins = [origin.strip() for origin in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"], 
)

# Registra routers
app.include_router(users.router)
app.include_router(auth.router)

