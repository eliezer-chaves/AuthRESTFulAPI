from fastapi import FastAPI
from routers import users, auth
from logging_config import logger
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aplicação iniciada com sucesso")
    yield
    logger.info("Aplicação encerrada")

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app = FastAPI(
    title="BaseAPI",
    description="API RESTful com autenticação JWT",
    version="1.0.0",
    lifespan=lifespan
)

# Atualize suas origins para incluir todas as portas possíveis
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Adicione outras portas que possa usar
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use a lista origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # IMPORTANTE: expõe headers
)

# Registra routers
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API is running"}
