import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate
from typing_extensions import Annotated

from database import get_db
from models import Message, Service, Survey, Template, Client
from models.company import Company

from models.utils.messageType import MessageType
from utils.get_company import validate_company_access
from service.email import send_email
from service.base_template_builder import base_template_builder
from schemas.messages import CreateMessage, SendFeedbackRequest, MessageOutput, MessagesOutput, ReviewResponse, SendRatingRequest, SendSurveyRequest

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/{company_id}/{client_id}/send_single_sms", response_model=MessagesOutput)
def create_sms_message(
    company_id: str,
    client_id: uuid.UUID,
    request: CreateMessage,
    db: Session = Depends(get_db),
    _: None = Depends(validate_company_access)
):
    message = Message(
        message=request.message,
        tracking_id=uuid.uuid4(),
        send_at=datetime.now(),
        messageType=MessageType.SMS,
        client_id=client_id,
        company_id=company_id
    )

    if request.isRedirect:
        message.is_redirect = True
    if request.platform:
        message.portal = request.platform
    if request.service:
        db_service = db.query(Service).filter_by(id=request.service).first()
        message.service = db_service
    if request.type == "feedback":
        message.is_feedback = True
        message.feedback_question = request.feedbackQuestion
    elif request.type == "rating":
        message.is_rating = True
        message.rating_question = request.ratingQuestion
    elif request.type == "survey":
        message.is_survey = True
        message.survey_id = request.surveyId

    db.add(message)
    db.commit()
    db.refresh(message)

    # TODO: Implement sending SMS

    return MessagesOutput(
        id=message.id,
        message=message.message,
        send_at=message.send_at,
        messageType=message.messageType.value if hasattr(message.messageType, "value") else message.messageType,
        responded=message.feedback_response.value if message.feedback_response else None,
        feedback=message.feedback_content,
        tracking_id=message.tracking_id,
    )


@router.post("/{company_id}/{client_id}/send_single_email", response_model=MessagesOutput)
def create_email_message(
    company_id: str,
    client_id: uuid.UUID,
    request: CreateMessage,
    db: Session = Depends(get_db),
    _: None = Depends(validate_company_access)
):
    message = Message(
        message=request.message,
        tracking_id=uuid.uuid4(),
        send_at=datetime.now(),
        messageType=MessageType.Email,
        client_id=client_id,
        company_id=company_id,
        template_id=request.template
    )

    if request.isRedirect:
        message.is_redirect = True
    if request.platform:
        message.portal = request.platform
    if request.service:
        db_service = db.query(Service).filter_by(id=request.service).first()
        message.service = db_service
    if request.type == "feedback":
        message.is_feedback = True
        message.feedback_question = request.feedbackQuestion
    elif request.type == "rating":
        message.is_rating = True
        message.rating_question = request.ratingQuestion
    elif request.type == "survey":
        message.is_survey = True
        message.survey_id = request.surveyId

    db.add(message)
    db.commit()
    db.refresh(message)

    template = db.query(Template).filter_by(id=request.template).first()
    user = db.query(Client).filter_by(id=client_id).first()
    company = db.query(Company).filter_by(id=company_id).first()

    if not template or not user or not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    template = str(template.template).replace('{{name}}', user.name.split(" ")[0]).replace("{{company}}", company.name)

    send_email("Acme <onboarding@resend.dev>", request.email, 'test', template)

    return MessagesOutput(
        id=message.id,
        message=message.message,
        send_at=message.send_at,
        messageType=message.messageType.value if hasattr(message.messageType, "value") else message.messageType,
        responded=message.feedback_response.value if message.feedback_response else None,
        feedback=message.feedback_content,
        tracking_id=message.tracking_id,
    )


@router.get("/{company_id}/{client_id}", response_model=Page[MessagesOutput], status_code=status.HTTP_200_OK)
def get_messages(
    company_id: uuid.UUID,
    client_id: uuid.UUID,
    search_term: Annotated[str | None, Query(max_length=100)] = None,
    params: Params = Depends(),
    db: Session = Depends(get_db),
    _: None = Depends(validate_company_access)
):
    query = db.query(Message).filter_by(client_id=client_id, company_id=company_id).order_by(Message.send_at.desc())

    if search_term:
        query = query.filter(Message.message.ilike(f"%{search_term}%"))

    return paginate(query, params)


@router.get("/review/{company_id}/{client_id}/{tracking_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
def get_review(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id).first()

    if message.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already completed"
        )

    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    service = db.query(Service).filter_by(id=message.service_id).first()
    company = db.query(Company).filter_by(id=company_id).first()
    review_link = None
    if message.portal:
        review_link = getattr(company, message.portal.value, None)

    review = ReviewResponse(
        service_name=service.name if service else None,
        service_id=service.id if service else None  ,
        company_logo=company.logo_url
    )
    if message.is_redirect:
        review.is_redirect = True
        review.portal = review_link if review_link else None
    if message.is_feedback:
        review.is_feedback = True
        review.feedback_question = message.feedback_question
    elif message.is_survey:
        survey = db.query(Survey).filter_by(id=message.survey_id).first()
        review.is_survey = True
        review.survey = survey
    elif message.is_rating:
        review.is_rating = True
        review.rating_question = message.rating_question

    return review


@router.get("/review/{company_id}/{client_id}/{tracking_id}/ping", status_code=status.HTTP_200_OK)
def ping_click(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id).first()
    if message.clicked_at or message.completed:
        return status.HTTP_200_OK
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    message.clicked_at = datetime.now()
    db.commit()
    db.refresh(message)
    return status.HTTP_200_OK

@router.post("/review/{company_id}/{client_id}/{tracking_id}/send_feedback", status_code=status.HTTP_201_CREATED)
def send_feedback(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        feedback: SendFeedbackRequest,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id).first()
    message.completed_at = datetime.now()
    # TODO: implement sentiment analysis
    #message.feedback_response = Respond.positiveResponse
    message.feedback_content = feedback.feedback
    message.completed = True
    db.commit()
    db.refresh(message)
    return status.HTTP_200_OK

@router.post("/review/{company_id}/{client_id}/{tracking_id}/send_rating", status_code=status.HTTP_201_CREATED)
def send_rating(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        rating: SendRatingRequest,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id).first()
    message.completed_at = datetime.now()
    message.rating = rating.rating
    message.rating_feedback = rating.feedback
    message.completed = True
    db.commit()
    db.refresh(message)
    return status.HTTP_200_OK

@router.post("/review/{company_id}/{client_id}/{tracking_id}/send_survey", status_code=status.HTTP_201_CREATED)
def send_survey(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        survey: SendSurveyRequest,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id, survey_id=survey.survey.survey_id).first()
    db_survey = db.query(Survey).filter_by(id=survey.survey.survey_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if not db_survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    if db_survey.completed_times is None:
        db_survey.completed_times = 1
    else:
        db_survey.completed_times = db_survey.completed_times + 1

    message.completed_at = datetime.now()
    message.survey_result = survey.survey.answers
    message.completed = True
    db.commit()
    db.refresh(message)
    db.refresh(db_survey)
    return status.HTTP_200_OK

@router.get("/review/{company_id}/{client_id}/sms_message_details/{message_id}", response_model=MessageOutput, status_code=status.HTTP_200_OK)
def sms_message_details(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        message_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, id=message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    service = None
    if message.service_id:
        service = db.query(Service).filter_by(id=message.service_id).first()

    survey_obj: Survey | None = None
    if message.is_survey:
        survey_obj = db.query(Survey).filter_by(id=message.survey_id).first()

    return MessageOutput(
        id=message.id,
        message=message.message,
        tracking_id=message.tracking_id,
        clicked_at=message.clicked_at,
        messageType=message.messageType,
        send_at=message.send_at,
        portal=message.portal,
        is_feedback=message.is_feedback,
        feedback_response=message.feedback_response,
        feedback_content=message.feedback_content,
        is_rating=message.is_rating,
        rating=message.rating,
        rating_feedback=message.rating_feedback,
        is_survey=message.is_survey,
        survey=survey_obj,
        survey_answer=message.survey_result,
        completed=message.completed,
        completed_at=message.completed_at,
        service_id=message.service_id,
        service_name=service.name if service else None,
        is_redirect=message.is_redirect
    )



