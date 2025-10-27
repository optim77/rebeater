import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Respond(enum.Enum):
    positiveResponse = "positiveResponse"
    negativeResponse = "negativeResponse"
    messageClicked = "messageClicked"


class MessageType(enum.Enum):
    Email = "email"
    SMS = "sms"


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invitation_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    message = Column(String, nullable=False)
    send_at = Column(DateTime, nullable=False)
    messageType = Column(Enum(MessageType, name="message_type_enum"), nullable=False)
    responded = Column(Enum(Respond, name="respond_enum"), nullable=True)
    feedback = Column(String, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)

    user = relationship("User", back_populates="messages")
    company = relationship("Company", back_populates="messages")

