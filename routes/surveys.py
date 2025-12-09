import uuid
from datetime import datetime
from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.survey import Survey
from utils.security import get_current_user
from models.company import Company

router = APIRouter(prefix="/surveys", tags=["surveys"])


class SurveyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    content: Any

class SurveyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class SurveyOutput(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    content: Any
    created_at: datetime | None = None
    updated_at: datetime | None = None

class CreateSurveyOutput(BaseModel):
    id: uuid.UUID
@router.post("/{company_id}/create", response_model=CreateSurveyOutput)
def create_survey(
        company_id: uuid.UUID,
        request: SurveyCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    survey = Survey(
        name=request.name,
        description=request.description,
        content=request.content,
        company_id=company.id
    )

    db.add(survey)
    db.commit()
    db.refresh(survey)

    return { "id": survey.id }

@router.get("/{company_id}/list", response_model=Page[SurveyOutput])
def get_surveys(
        company_id: uuid.UUID,
        search: str | None = Query(None),
        params: Params = Depends(),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    query = db.query(Survey).order_by(Survey.created_at.desc())

    if search:
        query = query.filter(Survey.name.ilike(f"%{search}%"))

    return paginate(query, params)


@router.get("/{company_id}/{survey_id}", response_model=SurveyOutput)
def get_single_survey(
        company_id: uuid.UUID,
        survey_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    survey = db.query(Survey).filter_by(id=survey_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    return survey

@router.put("/{company_id}/{survey_id}", response_model=CreateSurveyOutput)
def update_survey(
        company_id: uuid.UUID,
        survey_id: uuid.UUID,
        request: SurveyUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    survey = db.query(Survey).filter_by(id=survey_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    if request.name is not None:
        survey.name = request.name

    if request.description is not None:
        survey.description = request.description

    if request.content is not None:
        survey.content = request.content

    db.commit()
    db.refresh(survey)

    return { "id": survey.id }


@router.delete("/{company_id}/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_survey(
        company_id: uuid.UUID,
        survey_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    survey = db.query(Survey).filter_by(id=survey_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    db.delete(survey)
    db.commit()

    return None
