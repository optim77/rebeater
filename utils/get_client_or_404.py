from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
import uuid
from models.client import Client


def get_client_or_404(db: Session, client_id: uuid.UUID, company_id: uuid.UUID) -> Type[Client]:
    client = db.query(Client).filter_by(id=client_id, company_id=company_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client
