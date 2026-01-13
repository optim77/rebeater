from sqlalchemy import Column, String, UUID, ForeignKey, func, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    template = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    public = Column(Boolean, default=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)

    company = relationship("Company", back_populates="templates")
    messages = relationship("Message", back_populates="template")
