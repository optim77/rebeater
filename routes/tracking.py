import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib

from database import get_db
from models import Message

router = APIRouter(prefix="/r", tags=["tracking"])
# TODO: make service to short and redirect links for google_review_link
@router.get("/{tracking_id}")
def track(tracking_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    pass
    # invitation = db.query(Message).filter(Message.tracking_id == tracking_id).first()
    # if not invitation:
    #     raise HTTPException(status_code=404, detail="Invite not found")
    #
    # ip = request.client.host
    # db.add(click)
    # invitation.clicked_at = datetime.utcnow()
    # db.commit()
    # return


@router.post("/{tracking_id}/{status}")
def track_feedback(tracking_id: str, status: str, feedback: Optional[str], db: Session = Depends(get_db)):
    pass
    # invitation = db.query(Message).filter(Message.tracking_id == tracking_id).first()
    # if not invitation:
    #     raise HTTPException(status_code=404, detail="Invite not found")
    #
    #
    # if status == 'positive':
    #     click.status = "positive"
    #     return RedirectResponse(url="https://maps.google.com")
    # else:
    #     click.status = "negative"
    #     if feedback:
    #         click.feedback = feedback
    #     db.commit()
    #     return