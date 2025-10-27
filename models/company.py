from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(5000), nullable=True)
    google_review_link = Column(String)
    facebook_url = Column(String)
    instagram_link = Column(String)
    linkedin_link = Column(String)
    tiktok_link = Column(String)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="companies")
    clients = relationship("Client", back_populates="company", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="company", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="company", cascade="all, delete-orphan")
