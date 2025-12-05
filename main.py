from fastapi import FastAPI
from routers import users
from logging_config import logger

app = FastAPI()

# registrar rotas
app.include_router(users.router)

@app.get("/")
def root():
    logger.info("Endpoint /test acessado!")
    return {"message": "API FastAPI funcionando 🚀"}
