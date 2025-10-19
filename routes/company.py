from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_pagination import Page, paginate, Params
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional
from models.company import Company
from database import get_db
from routes.utils import PaginatedResponse
from utils.security import get_current_user
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/companies", tags=["Companies"])

class CompanyCreate(BaseModel):
    name: str
    description: str = None

class CompanyUpdate(BaseModel):
    name: str = None
    description: str = None

class CompanyOut(BaseModel):
    id: UUID
    name: str
    description: str = None
    owner_id: UUID

    class Config:
        orm_mode = True



@router.post("/", response_model=CompanyOut)
def create_company(company: CompanyCreate,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    db_company = Company(
        name=company.name,
        description=company.description,
        owner_id=current_user.id
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/", response_model=Page[CompanyOut])
def list_companies(
    search_term: Optional[str] = Query(None),
    params: Params = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Company).filter(Company.owner_id == current_user.id)

    if search_term:
        query = query.filter(
            or_(
                Company.name.ilike(f"%{search_term}%"),
                Company.description.ilike(f"%{search_term}%")
            )

        )

    return paginate(query, params)


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: UUID,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=CompanyOut)
def update_company(company_id: UUID,
                   company_update: CompanyUpdate,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if company_update.name is not None:
        company.name = company_update.name
    if company_update.description is not None:
        company.description = company_update.description

    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: UUID,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    db.delete(company)
    db.commit()
    return
