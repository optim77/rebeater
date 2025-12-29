import uuid

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.survey import Survey
from utils.get_company import validate_company_access
from utils.security import get_current_user
from models.company import Company
from schemas.surveys import CreateSurveyOutput, SurveyCreate, SurveyOutput, SurveyUpdate

router = APIRouter(prefix="/surveys", tags=["surveys"])

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
        _: None = Depends(validate_company_access)
):
    query = db.query(Survey).order_by(Survey.created_at.desc())

    if search:
        query = query.filter(Survey.name.ilike(f"%{search}%"))

    return paginate(query, params)


@router.get("/{company_id}/{survey_id}", response_model=SurveyOutput)
def get_single_survey(
        company_id: uuid.UUID,
        survey_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
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
        _: None = Depends(validate_company_access)
):
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
        _: None = Depends(validate_company_access)
):
    survey = db.query(Survey).filter_by(id=survey_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    db.delete(survey)
    db.commit()

    return None
