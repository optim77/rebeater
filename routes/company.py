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
from schemas.company import GroupOut, GroupCreate, GroupUpdate

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
        group: GroupCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):

    db_group = Company(
        name=group.name,
        description=group.description,
        owner_id=current_user.id,
        google=group.google_review_link,
        facebook=group.facebook_url,
        instagram=group.instagram_link,
        linkedin=group.linkedin_link,
        tiktok=group.tiktok_link,
        znany_lekarz=group.znany_lekarz,
        booksy=group.booksy_link,
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


@router.get("/", response_model=Page[GroupOut], status_code=status.HTTP_200_OK)
def list_groups(
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


@router.get("/{group_id}", response_model=GroupOut, status_code=status.HTTP_200_OK)
def get_company(
        group_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):
    group = db.query(Company).filter_by(id=group_id,owner_id=current_user.id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return group


@router.get("/{group_id}/socials")
def get_socials(
        group_id: uuid.UUID,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    group = db.query(Company).filter_by(id=group_id, owner_id=current_user.id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return {
        "google": group.google,
        "facebook": group.facebook,
        "instagram": group.instagram,
        "tiktok": group.tiktok,
        "linkedin": group.linkedin,
        "booksy": group.booksy,
        "znany_lekarz": group.znany_lekarz
    }


@router.put("/{group_id}", response_model=GroupOut)
def update_group(
        group_id: UUID,
        group_update: GroupUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):

    group = db.query(Company).filter_by(id=group_id, owner_id=current_user.id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if group_update.name is not None:
        group.name = group_update.name
    if group_update.description is not None:
        group.description = group_update.description
    if group_update.facebook_url is not None:
        group.facebook_url = group_update.facebook_url
    if group_update.instagram_link is not None:
        group.instagram_link = group_update.instagram_link
    if group_update.linkedin_link is not None:
        group.linkedin_link = group_update.linkedin_link
    if group_update.tiktok_link is not None:
        group.tiktok_link = group_update.tiktok_link
    if group_update.znany_lekarz is not None:
        group.znany_lekarz = group_update.znany_lekarz
    if group_update.booksy_link is not None:
        group.booksy_link = group_update.booksy_link

    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
        group_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)):
    group = db.query(Company).filter_by(id=group_id, owner_id=current_user.id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    db.delete(group)
    db.commit()
    return
