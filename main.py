from fastapi import FastAPI
from routers.auth import accounts_router, password_resets_router, sessions_router
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
    title="Auth API",
    description="RESTful authentication API built with FastAPI, providing secure user authentication using JWT, email verification, and password recovery flows.",
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

app.include_router(sessions_router.router)
app.include_router(accounts_router.router)
app.include_router(password_resets_router.router)

