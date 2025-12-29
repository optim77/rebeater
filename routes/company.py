import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional
from models.company import Company
from database import get_db
from utils.security import get_current_user
from uuid import UUID
from schemas.company import CompanyOut, CompanyCreate, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
        company: CompanyCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):

    db_company = Company(
        name=company.name,
        description=company.description,
        owner_id=current_user.id,
        google=company.google_review_link,
        facebook=company.facebook_url,
        instagram=company.instagram_link,
        linkedin=company.linkedin_link,
        tiktok=company.tiktok_link,
        znany_lekarz=company.znany_lekarz,
        booksy=company.booksy_link,
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.get("/", response_model=Page[CompanyOut], status_code=status.HTTP_200_OK)
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


@router.get("/{company_id}", response_model=CompanyOut, status_code=status.HTTP_200_OK)
def get_company(
        company_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):
    company = db.query(Company).filter_by(id=company_id,owner_id=current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.get("/{company_id}/socials")
def get_socials(
        company_id: uuid.UUID,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    company = db.query(Company).filter_by(id=company_id, owner_id=current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return {
        "google": company.google,
        "facebook": company.facebook,
        "instagram": company.instagram,
        "tiktok": company.tiktok,
        "linkedin": company.linkedin,
        "booksy": company.booksy,
        "znany_lekarz": company.znany_lekarz
    }


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
        company_id: UUID,
        company_update: CompanyUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):

    company = db.query(Company).filter_by(id=company_id, owner_id=current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if company_update.name is not None:
        company.name = company_update.name
    if company_update.description is not None:
        company.description = company_update.description
    if company_update.facebook_url is not None:
        company.facebook_url = company_update.facebook_url
    if company_update.instagram_link is not None:
        company.instagram_link = company_update.instagram_link
    if company_update.linkedin_link is not None:
        company.linkedin_link = company_update.linkedin_link
    if company_update.tiktok_link is not None:
        company.tiktok_link = company_update.tiktok_link
    if company_update.znany_lekarz is not None:
        company.znany_lekarz = company_update.znany_lekarz
    if company_update.booksy_link is not None:
        company.booksy_link = company_update.booksy_link

    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
        company_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):
    company = db.query(Company).filter_by(id=company_id, owner_id=current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    db.delete(company)
    db.commit()
    return
