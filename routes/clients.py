from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi_pagination import Page, paginate, Params
from pydantic import BaseModel
from sqlalchemy.orm import Session

import uuid

from sqlalchemy import or_
from starlette import status

from database import get_db
from models.client import Client
from models.company import Company
from utils.security import get_current_user

router = APIRouter(prefix="/clients", tags=["clients"])

class CreateClient(BaseModel):
    name: str
    email: str
    phone: str
    company: uuid.UUID

class ClientOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: str
    company: uuid.UUID

    class Config:
        from_attributes = True


@router.post("/")
def add_client(client: CreateClient, db: Session =Depends(get_db)):
    client = Client(id=uuid.uuid4(), name=client.name, email=client.email, phone=client.phone, company_id=client.company.id)
    db.add(client)
    db.commit()
    return client

@router.get("/{company_id}", response_model=Page[ClientOut])
def list_clients(
        company_id: uuid.UUID,
        search_term: str = Query(None),
        params: Params = Depends(),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):

    # TODO: Get out this function to generic one
    company = db.query(Company).filter(Company.id == company_id,Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")


    query = db.query(Client).filter(Client.company_id == company_id)

    if search_term:
        query = query.filter(
            or_(
                Client.name.ilike(f"%{search_term}%"),
                Client.email.ilike(f"%{search_term}%"),
                Client.phone.ilike(f"%{search_term}%"),
            )
        )

    return paginate(query, params)

@router.get("/{company_id}/{client_id}", response_model=ClientOut)
def get_client(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id,Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return client

@router.put("/{company_id}/{client_id}", response_model=ClientOut)
def update_client(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        client_update: CreateClient,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    company = db.query(Company).filter(Company.id == company_id, Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    for key, value in client_update.dict().items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{company_id}/{client_id}")
def delete_client(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)):


    company = db.query(Company).filter(Company.id == company_id, Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"detail": "Client deleted successfully"}
