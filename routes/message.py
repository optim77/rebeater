import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.company import Company
from utils.security import get_current_user


class CreateMessage(BaseModel):
    message: str
    messageType: str
    user_id: str


class MessageOutput(BaseModel):
    id: uuid.UUID
    invitation_id: uuid.UUID
    message: str
    send_at: datetime.datetime
    messageType: str
    responded: str
    feedback: str



router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/{company_id}/{client_id}", response_model=MessageOutput)
async def create_message(
        company_id: str,
        client_id: str,
        request: CreateMessage,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)):

    company = db.query(Company).filter(Company.id == company_id, Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    invitation_id = uuid.uuid4()


