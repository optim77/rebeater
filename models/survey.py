from sqlalchemy import Column, UUID, String, JSON, DateTime, func, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship

from database import Base
import uuid

class Survey(Base):
    __tablename__ = 'surveys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content = Column(JSON, nullable=False)
    completed_times = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # TODO: Make logic for that
    # link_end_date = Column(DateTime(timezone=True), server_default=func.now())
    # end_date = Column(DateTime(timezone=True), server_default=func.now())
    # allow_multiple = Column(Boolean, default=True)
    # active = Column(Boolean, default=True)
    # max_limit_response = Column(Integer, nullable=True)
    

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    messages = relationship("Message", back_populates="survey", cascade="all, delete-orphan")
    company = relationship("Company", back_populates="surveys")
    survey_analytic = relationship("SurveyAnalytic", back_populates="survey", uselist=False, cascade="all, delete-orphan")
