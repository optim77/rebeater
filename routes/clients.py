from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import uuid

from database import get_db
from models.client import Client

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/")
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

@router.post("/")
def add_client(name: str, email: str = None, phone: str = None, db: Session = Depends(get_db)):
    client = Client(id=uuid.uuid4(), name=name, email=email, phone=phone)
    db.add(client)
    db.commit()
    return {"message": "Client added"}
