from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(5000))
    logo_url = Column(String(5000), nullable=True)


    google = Column(String)
    facebook = Column(String)
    instagram = Column(String)
    linkedin = Column(String)
    tiktok = Column(String)
    znany_lekarz = Column(String)
    booksy = Column(String)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="companies")
    clients = relationship("Client", back_populates="company", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="company", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="company", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="company", cascade="all, delete-orphan")
    surveys = relationship("Survey", back_populates="company", cascade="all, delete-orphan")
