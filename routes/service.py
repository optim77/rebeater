import uuid

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from fastapi_pagination import Params
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate
from database import get_db
from models.company import Company
from models.services import Service
from utils.security import get_current_user

router = APIRouter(prefix="/services", tags=["service"])

class CreateService(BaseModel):
    name: str
    description: str

class ServiceOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    company_id: uuid.UUID

    class Config:
        from_attribute = True

@router.get("/{company_id}/{service_id}", response_model=ServiceOut)
def get_service(
        company_id: uuid.UUID,
        service_id: uuid.UUID,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id,Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    client = db.query(Service).filter(Service.id == service_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    return client


@router.get("/${company_id}", response_model=ServiceOut)
def list_services(
        company_id: uuid.UUID,
        search_term: str = Query(None),
        params: Params = Depends(),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    company = db.query(Company).filter(Company.id == company_id, Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    query = db.query(Service).filter(Service.company_id == company_id)

    if search_term:
        query = query.filter(
            or_(
                Service.name.ilike(f"%{search_term}%"),
                Service.description.ilike(f"%{search_term}%"),
            )
        )

    return paginate(query, params)


@router.post("/{company_id}", response_model=ServiceOut)
def add_service(company_id: str, service: CreateService, db: Session = Depends(get_db)):
    service = Service(id=uuid.uuid4(), name=service.name, description=service.description, company_id=company_id)
    db.add(service)
    db.commit()
    return service


@router.put("/{company_id}/{service_id}", response_model=ServiceOut)
def update_client(
        company_id: uuid.UUID,
        service_id: uuid.UUID,
        service_update: CreateService,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    company = db.query(Company).filter(Company.id == company_id, Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    for key, value in service_update.dict().items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{company_id}/{service_id}")
def delete_service(
        company_id: uuid.UUID,
        service_id: uuid.UUID,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)):


    company = db.query(Company).filter(Company.id == company_id, Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    db.delete(service)
    db.commit()
    return {"detail": "Service deleted successfully"}