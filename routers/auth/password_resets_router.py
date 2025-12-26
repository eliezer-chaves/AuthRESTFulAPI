from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas.user_schema import UserEmail
from core.services.auth import password_reset_service

router = APIRouter(
    prefix="/password-resets",
    tags=["Password Reset Flow"]
)

@ router.post("")
async def request_password_reset_route(payload: UserEmail, response: Response, request: Request, db: Session=Depends(get_db)):
   return await password_reset_service.request_password_reset(payload, response, request, db)

@ router.post("/verification")
def verify_reset_code_route(body: dict, response: Response, request: Request, db: Session=Depends(get_db)):
    return password_reset_service.verify_reset_code(body, response, request, db)

@ router.get("/authorization")
def authorize_password_reset_route(request: Request, db: Session=Depends(get_db)):
    return password_reset_service.authorize_password_reset(request, db)

@ router.get("/status")
def get_password_reset_status_route(request: Request, db: Session=Depends(get_db)):
    return password_reset_service.get_password_reset_status(request, db)

@ router.patch("")
def update_password_route(body: dict, request: Request, response: Response, db: Session=Depends(get_db)):
    return password_reset_service.update_password(body, request, response, db)
    