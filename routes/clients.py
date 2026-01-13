from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

import uuid
from sqlalchemy import or_
from starlette import status

from database import get_db
from models.client import Client
from utils.db_transaction import db_transaction
from utils.get_client_or_404 import get_client_or_404
from utils.get_company import validate_company_access
from schemas.clients import CreateClient, ClientOut, UpdateClient

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/{company_id}", status_code=status.HTTP_201_CREATED)
def add_client(company_id: uuid.UUID, client: CreateClient, db: Session = Depends(get_db)):
    client = Client(id=uuid.uuid4(), name=client.name, surname=client.surname, email=client.email, phone=client.phone, company_id=company_id)
    with db_transaction(db):
        db.add(client)
    return client


@router.get("/{company_id}", response_model=Page[ClientOut], status_code=status.HTTP_200_OK)
def list_clients(
        company_id: uuid.UUID,
        search_term: str = Query(None),
        params: Params = Depends(),
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
    query = db.query(Client).filter_by(company_id=company_id).order_by(Client.name)

    if search_term:
        query = query.filter(
            or_(
                Client.name.ilike(f"%{search_term}%"),
                Client.surname.ilike(f"%{search_term}%"),
                Client.email.ilike(f"%{search_term}%"),
                Client.phone.ilike(f"%{search_term}%"),
            )
        )

    return paginate(query, params)


@router.get("/{company_id}/{client_id}", response_model=ClientOut, status_code=status.HTTP_200_OK)
def get_client(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
    client = get_client_or_404(db, client_id, company_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return client

@router.put("/{company_id}/{client_id}", response_model=ClientOut, status_code=status.HTTP_200_OK)
def update_client(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        client_update: UpdateClient,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):

    client = get_client_or_404(db, client_id, company_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    for key, value in client_update.dict(exclude_unset=True).items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{company_id}/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):

    client = get_client_or_404(db, client_id, company_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"detail": "Client deleted successfully"}
