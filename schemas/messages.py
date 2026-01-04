from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, conint
import uuid

from models.utils.portalType import Portal
from models.utils.respondType import Respond
from schemas.common.types import ClientPhone, ClientEmail

FEEDBACK_TYPE = "feedback"
RATING_TYPE = "rating"
SURVEY_TYPE = "survey"


class CreateMessage(BaseModel):
    message: str
    phone: ClientPhone
    email: ClientEmail | None = None
    service: uuid.UUID | None = None
    platform: Portal | None = None
    type: str = FEEDBACK_TYPE or RATING_TYPE or SURVEY_TYPE
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


class SurveyResponse(BaseModel):
    id: uuid.UUID
    name: str | None = None
    description: str | None = None
    content: dict | None = None

    model_config = {
        "from_attributes": True
    }


class ReviewResponse(BaseModel):
    service_name: str | None = None
    service_id: uuid.UUID | None = None
    portal: str | None = None
    is_feedback: bool | None = None
    feedback_question: str | None = None
    is_survey: bool | None = None
    survey: SurveyResponse | None = None
    is_rating: bool | None = None
    is_redirect: bool | None = None
    rating_question: str | None = None
    company_logo: str | None = None


class URLFeedbackResponse(BaseModel):
    status: str = "positive" or "negative"
    feedback: str | None = None


class SendFeedbackRequest(BaseModel):
    feedback: str | None = None


class SendRatingRequest(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    feedback: str | None = None


class CompletedSurveyRequest(BaseModel):
    survey_id: uuid.UUID
    answers: dict[str, str | int]


class SendSurveyRequest(BaseModel):
    survey: CompletedSurveyRequest | None = None


class SurveyQuestionResponse(BaseModel):
    id: uuid.UUID
    type: str
    label: str
    required: bool
    options: list[str] | None = None


class SurveyDetailsResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    content: list[SurveyQuestionResponse]
    model_config = {
        "from_attributes": True
    }


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
    survey: SurveyDetailsResponse | None = None
    survey_answer: Optional[dict[str, str | int]]
    completed: bool | None = None
    completed_at: datetime | None = None
    service_id: uuid.UUID | None = None
    service_name: str | None = None
    is_redirect: bool | None = None
