from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from database import Base

class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    message = Column(String)
    channel = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    clicked_at = Column(DateTime, nullable=True)
    tracking_id = Column(UUID(as_uuid=True))
