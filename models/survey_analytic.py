import uuid

from sqlalchemy import Column, UUID, ForeignKey, DateTime, func, JSON, Integer
from sqlalchemy.orm import relationship

from database import Base


class SurveyAnalytic(Base):
    __tablename__ = 'survey_analytic'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    content = Column(JSON, nullable=False)
    completed_times = Column(Integer, nullable=False)

    survey = relationship("Survey", back_populates="survey_analytic")

