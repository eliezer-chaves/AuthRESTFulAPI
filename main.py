from fastapi import FastAPI
from routers import users
from routers import auth
from logging_config import logger

app = FastAPI(
    title="BaseAPI",
    description="API RESTful com autenticação JWT",
    version="1.0.0"
)

# Registra routers
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/", tags=["Health"])
def health_check():
    """
    Verifica se a API está funcionando.
    """
    return {"status": "ok", "message": "API is running"}

@app.on_event("startup")
async def startup_event():
    logger.info("Aplicação iniciada com sucesso")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Aplicação encerrada")