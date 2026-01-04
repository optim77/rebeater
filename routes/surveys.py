import uuid

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.testing.suite.test_reflection import users
from starlette import status

from database import get_db
from models import SurveyAnalytic, Message, Client
from models.survey import Survey
from utils.get_company import validate_company_access
from utils.security import get_current_user
from models.company import Company
from schemas.surveys import CreateSurveyOutput, SurveyCreate, SurveyOutput, SurveyUpdate, SurveyAnalyticsData

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
        survey_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
    survey = db.query(Survey).filter_by(id=survey_id).first()
    survey_analysis = db.query(SurveyAnalytic).filter_by(id=survey_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    db.delete(survey)
    db.delete(survey_analysis)
    db.commit()

    return None

@router.get("/{company_id}/{survey_id}/analytic", response_model=SurveyAnalyticsData, status_code=status.HTTP_200_OK)
def get_analytics(
        survey_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
    survey = db.query(Survey).filter_by(id=survey_id).first()

    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey_analytics = db.query(SurveyAnalytic).filter_by(survey_id=survey_id).first()
    if survey_analytics is None or survey_analytics.completed_times != survey.completed_times:
        analysis_id, all_users = do_analytics(survey, survey_analytics, db)
        analysis = db.query(SurveyAnalytic).filter_by(id=analysis_id).first()
        print(analysis.completed_times)
        return SurveyAnalyticsData(
            id=analysis.id,
            survey_id=survey.id,
            name=survey.name,
            description=survey.description,
            content=analysis.content,
            completed_times=analysis.completed_times,
            users=all_users
        )
    elif survey_analytics.completed_times == survey.completed_times:
        all_users = dict()
        messages = db.query(Message).filter_by(is_survey=True, survey_id=survey.id).all()
        for message in messages:
            client = db.query(Client).filter_by(id=message.client_id).first()
            all_users.update({client.id: client.email})
        return SurveyAnalyticsData(
            id=survey_analytics.id,
            survey_id=survey.id,
            name=survey.name,
            description=survey.description,
            content=survey_analytics.content,
            completed_times=survey_analytics.completed_times,
            users=all_users
        )

class SurveyAnswer(BaseModel):
    client_id: uuid.UUID
    client_email: str
    answer: str | int

class SurveyAnalyticRecord(BaseModel):
    type: str
    label: str
    required: bool
    options: list[str] | None = None
    average_rating: float | None = None
    average_choice: dict[str, int] = Field(default_factory=dict)
    answers: list[SurveyAnswer] = Field(default_factory=list)

class SurveyAnalyticOutput(BaseModel):
    records: list[SurveyAnalyticRecord]

def do_analytics(
        survey: Survey,
        survey_analytics: SurveyAnalytic | None,
        db: Session = Depends(get_db),
):
    messages = db.query(Message).filter_by(is_survey=True, survey_id=survey.id).all()
    analytic: SurveyAnalyticOutput = SurveyAnalyticOutput(total_answers=len(messages), records=[])
    all_users = dict()
    for s in survey.content:
        record = SurveyAnalyticRecord(type=s.get('type'), label=s.get('label'), required=s.get('required'), options=s.get('options'))
        ratings = 0
        counter_rating = 0
        if s.get('type') == 'choice':
            options = s.get('options')
            for option in options:
                record.average_choice[str(option)] = 0

        for message in messages:
            if s['id'] is not None and message.survey_result is not None:
                if s.get('type') == 'rating':
                    counter_rating += 1
                    ratings += message.survey_result[s['id']]
                if s.get('type') == 'choice':
                    record.average_choice[message.survey_result[s['id']]] += 1
                client = db.query(Client).filter_by(id=message.client_id).first()
                all_users.update({client.id: client.email})
                answer = SurveyAnswer(client_id=client.id, client_email=client.email, answer=message.survey_result[s['id']])

                record.answers.append(answer)
        if ratings > 0 and counter_rating > 0:
            record.average_rating = ratings / counter_rating
        analytic.records.append(record)

    if survey_analytics is not None:
        survey_analytics.content = analytic.model_dump(mode="json")
        survey_analytics.completed_times = len(messages)
        db.add(survey_analytics)
        db.commit()
        return survey_analytics.id, all_users
    else:
        analysis = SurveyAnalytic(
            survey_id=survey.id,
            content=analytic.model_dump(mode="json"),
            completed_times=len(messages),
        )
        db.add(analysis)
        db.commit()
        return analysis.id, all_users

