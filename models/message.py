import uuid

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean, UUID, JSON
from sqlalchemy.orm import relationship

from database import Base
from models.utils.messageType import MessageType
from models.utils.portalType import Portal
from models.utils.respondType import Respond


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(String, nullable=False)
    tracking_id = Column(UUID(as_uuid=True))
    send_at = Column(DateTime, nullable=False)
    clicked_at = Column(DateTime, nullable=True)
    messageType = Column(Enum(MessageType, name="message_type_enum"), nullable=False)


    is_feedback = Column(Boolean, nullable=True)
    feedback_question = Column(String, nullable=True)
    feedback_response = Column(Enum(Respond, name="respond_enum"), nullable=True)
    feedback_content = Column(String, nullable=True)

    is_rating = Column(Boolean, nullable=True)
    rating_question = Column(String, nullable=True)
    rating = Column(String, nullable=True)
    rating_feedback = Column(String, nullable=True)

    is_survey = Column(Boolean, nullable=True)
    survey_result = Column(JSON, nullable=True)

    is_redirect = Column(Boolean, nullable=True)
    portal = Column(Enum(Portal, name="portal_enum"), nullable=True)


    completed = Column(Boolean, nullable=True, default=False)
    completed_at = Column(DateTime, nullable=True)


    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=True)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=True)

    client = relationship("Client", back_populates="messages")
    company = relationship("Company", back_populates="messages")
    service = relationship("Service", back_populates="messages")
    survey = relationship("Survey", back_populates="messages")
    template = relationship("Template", back_populates="messages")

