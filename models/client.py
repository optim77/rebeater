from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    email = Column(String(255))
    phone = Column(String(20))
    service = Column(String(255))
    note = Column(String(1000))
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    company = relationship("Company", back_populates="clients")
    messages = relationship("Message", back_populates="client", cascade="all, delete-orphan")