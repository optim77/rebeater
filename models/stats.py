from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
import uuid

class Stats(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    company = relationship("Company", back_populates="services")