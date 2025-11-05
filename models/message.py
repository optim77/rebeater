import uuid

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.utils.messageType import MessageType
from models.utils.portalType import Portal
from models.utils.respondType import Respond


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(String, nullable=False)
    send_at = Column(DateTime, nullable=False)
    messageType = Column(Enum(MessageType, name="message_type_enum"), nullable=False)
    responded = Column(Enum(Respond, name="respond_enum"), nullable=True)
    portal = Column(Enum(Portal, name="portal_enum"), nullable=True)
    feedback = Column(String, nullable=True)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)

    client = relationship("Client", back_populates="messages")
    company = relationship("Company", back_populates="messages")
    invitation = relationship("Invitation", back_populates="message", uselist=False)

