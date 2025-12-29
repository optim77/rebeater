import uuid
from datetime import datetime

from pydantic import BaseModel
from typing import Any
class SurveyCreate(BaseModel):
    name: str
    description: str | None = None
    content: Any

class SurveyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    content: Any | None = None

class SurveyOutput(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    content: Any
    created_at: datetime | None = None
    updated_at: datetime | None = None

class CreateSurveyOutput(BaseModel):
    id: uuid.UUID