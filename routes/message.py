from fastapi import APIRouter
from pydantic import BaseModel


class CreateMessage(BaseModel):
    message: str
    messageType: str
    user_id: str


router = APIRouter(prefix="/messages", tags=["messages"])