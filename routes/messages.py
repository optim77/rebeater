import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_pagination import Page, Params
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate
from database import get_db
from models import Message, Service
from models.company import Company

from models.utils.messageType import MessageType
from models.utils.portalType import Portal
from models.utils.respondType import Respond
from utils.security import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

class CreateMessage(BaseModel):
    message: str
    phone: str
    service: Optional[uuid.UUID] = None
    platform: str
    type: str = "feedback" or "rating" or "survey"
    isRedirect: bool = False
    ratingQuestion: str | None = None
    feedbackQuestion: str | None = None
    surveyId: uuid.UUID | None = None

    @field_validator("service", mode="before")
    def empty_string_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

class MessagesOutput(BaseModel):
    id: uuid.UUID
    message: str
    send_at: datetime
    messageType: str
    clicked_at: datetime | None = None
    feedback_content: str | None = None
    tracking_id: uuid.UUID | None = None
    is_feedback: bool | None = None
    is_rating: bool | None = None
    is_survey: bool | None = None
    feedback_response: Respond | None = None
    completed: bool | None = None
    completed_at: datetime | None = None

class ReviewResponse(BaseModel):
    service_name: str | None = None
    service_id: uuid.UUID | None = None
    portal: str | None = None
    is_feedback: bool | None = None
    is_survey: bool | None = None
    is_rating: bool | None = None
    company_logo: str | None = None

class URLFeedbackResponse(BaseModel):
    status: str = "positive" or "negative"
    feedback: str | None = None


class MessageOutput(BaseModel):
    id: uuid.UUID
    message: str
    tracking_id: uuid.UUID | None = None
    clicked_at: datetime | None = None
    messageType: str
    send_at: datetime
    portal: Portal | None = None
    is_feedback: bool | None = None
    feedback_response: Respond | None = None
    feedback_content: str | None = None
    is_rating: bool | None = None
    rating: int | None = None
    rating_feedback: str | None = None
    is_survey: bool | None = None
    completed: bool | None = None
    completed_at: datetime | None = None
    service_id: uuid.UUID | None = None
    service_name: str | None = None

@router.post("/{company_id}/{client_id}/send_single_sms", response_model=MessagesOutput)
def create_message(
    company_id: str,
    client_id: uuid.UUID,
    request: CreateMessage,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    message = Message(
        message=request.message,
        tracking_id=uuid.uuid4(),
        send_at=datetime.now(),
        messageType=MessageType.SMS,
        client_id=client_id,
        company_id=company.id
    )
    if request.platform:
        message.platform = Portal[request.platform]
    if request.service:
        message.service = request.service
    if request.type == "feedback":
        message.is_feedback = True
        message.feedback_question = request.feedbackQuestion
    elif request.type == "rating":
        message.is_rating = True
        message.rating_question = request.ratingQuestion
    elif request.type == "survey":
        message.is_survey = True
        message.survey_id = request.surveyId


    db.add_all([message])
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


@router.get("/{company_id}/{client_id}", response_model=Page[MessagesOutput], status_code=status.HTTP_200_OK)
def get_messages(
    company_id: uuid.UUID,
    client_id: uuid.UUID,
    search_term: str | None = Query(None),
    params: Params = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company = (db.query(Company).filter_by(id=company_id, owner_id=current_user.id).first())
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

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

    review_link = getattr(company, message.portal.value, None)
    if not review_link:
        raise HTTPException(status_code=404, detail="No review link found for this portal")

    return ReviewResponse(
        service_name=service.name if service else None,
        service_id=service.id if service else None  ,
        portal=review_link,
        is_feedback=message.is_feedback,
        is_survey=message.is_survey,
        is_rating=message.is_rating,
        company_logo=company.logo_url
    )


@router.get("/review/{company_id}/{client_id}/{tracking_id}/ping")
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

@router.post("/review/{company_id}/{client_id}/{tracking_id}/url_feedback_positive")
def url_feedback_positive(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id).first()
    message.completed_at = datetime.now()
    message.feedback_response = Respond.positiveResponse
    message.completed = True
    db.commit()
    db.refresh(message)
    return status.HTTP_200_OK


@router.post("/review/{company_id}/{client_id}/{tracking_id}/url_feedback_negative")
def url_feedback_negative(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        tracking_id: uuid.UUID,
        feedback: URLFeedbackResponse,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(client_id=client_id, company_id=company_id, tracking_id=tracking_id).first()
    message.completed_at = datetime.now()
    message.feedback_response = Respond.negativeResponse
    if feedback.feedback:
        message.feedback_content = feedback.feedback
    message.completed = True
    db.commit()
    db.refresh(message)
    return status.HTTP_200_OK


@router.get("/review/{company_id}/{client_id}/sms_message_details/{message_id}", response_model=MessageOutput)
def sms_message_details(
        company_id: uuid.UUID,
        client_id: uuid.UUID,
        message_id: uuid.UUID,
        db: Session = Depends(get_db),
):
    message = db.query(Message).filter_by(
        client_id=client_id,
        company_id=company_id,
        id=message_id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    service = None
    if message.service_id:
        service = db.query(Service).filter_by(id=message.service_id).first()

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
        completed=message.completed,
        completed_at=message.completed_at,
        service_id=message.service_id,
        service_name=service.name if service else None,
    )



