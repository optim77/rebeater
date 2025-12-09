from sqlalchemy import Column, UUID, String, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
import uuid

class Survey(Base):
    __tablename__ = 'surveys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    messages = relationship("Message", back_populates="survey", cascade="all, delete-orphan")
    company = relationship("Company", back_populates="surveys")
