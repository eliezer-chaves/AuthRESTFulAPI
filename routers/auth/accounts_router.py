from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas.user_schema import UserCreate
from core.services.auth import auth_service

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

@router.post("", status_code=201)
async def create_user_route(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    return await auth_service.create_user(payload, response, db)

@router.post("/verification")
def validate_account_route(body: dict, response: Response, db: Session = Depends(get_db)):
   return auth_service.validate_account(body, response, db)
    
@router.get("/verification/status")
def check_email_status_route(request: Request, db: Session = Depends(get_db)):
    return auth_service.check_email_status(request, db)
    
    

