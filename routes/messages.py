import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import Message
from models.company import Company
from models.invitation import Invitation
from utils.security import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

class CreateMessage(BaseModel):
    message: str
    messageType: str
    platform: str
    service: uuid.UUID


class MessageOutput(BaseModel):
    id: uuid.UUID
    message: str
    send_at: datetime
    messageType: str
    responded: str | None = None
    feedback: str | None = None
    invitation_id: uuid.UUID | None = None


@router.post("/{company_id}/{client_id}/send_single_sms", response_model=MessageOutput)
def create_message(
    company_id: str,
    client_id: str,
    request: CreateMessage,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    company = (
        db.query(Company)
        .filter(Company.id == company_id, Company.owner_id == current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")


    message = Message(
        message=request.message,
        send_at=datetime.now(),
        messageType=request.messageType,
        portal=request.social,
        client_id=client_id,
        company_id=company.id,
    )


    invitation = Invitation(
        sent_at=datetime.now(),
        tracking_id=uuid.uuid4(),
        social_link=request.social,
        client_id=client_id,
        message_id=message,
    )

    db.add_all([message, invitation])
    db.commit()

    db.refresh(message)
    db.refresh(invitation)

    return MessageOutput(
        id=message.id,
        message=message.message,
        send_at=message.send_at,
        messageType=message.messageType.value if hasattr(message.messageType, "value") else message.messageType,
        responded=message.responded.value if message.responded else None,
        feedback=message.feedback,
        invitation_id=invitation.id,
    )
