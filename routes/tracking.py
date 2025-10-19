from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib

from database import get_db
from models.click import Click
from models.invitation import Invitation

router = APIRouter(prefix="/r", tags=["tracking"])
# TODO: make service to short and redirect links for google_review_link
@router.get("/{invite_id}")
def track(invite_id: str, request: Request, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.id == invite_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invite not found")

    ip = request.client.host
    click = Click(invitation_id=invite_id, ip_hash=hashlib.sha256(ip.encode()).hexdigest())
    db.add(click)
    invitation.clicked_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url="https://maps.google.com")  # tu w V2: firma.google_review_link
