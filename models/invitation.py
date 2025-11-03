from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from sqlalchemy.orm import relationship

from database import Base

class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sent_at = Column(DateTime, default=datetime.utcnow)
    clicked_at = Column(DateTime, nullable=True)
    tracking_id = Column(UUID(as_uuid=True))
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    social_link = Column(String, nullable=False)

    client = relationship("Client", back_populates="invitation")
    message = relationship("Message", back_populates="invitation")
