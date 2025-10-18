from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import uuid

from database import get_db
from models.invitation import Invitation

router = APIRouter(prefix="/invitations", tags=["invitations"])

@router.post("/send")
def send_invitation(client_id: str, message: str, db: Session = Depends(get_db)):
    invitation = Invitation(
        id=uuid.uuid4(),
        client_id=client_id,
        company_id=None,
        message=message,
        channel="email"
    )
    db.add(invitation)
    db.commit()
    return {"invite_link": f"https://yourapp.com/r/{invitation.id}"}
