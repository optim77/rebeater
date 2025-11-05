from sqlalchemy import Column, String, Enum, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from models.utils.messageType import MessageType
import uuid

class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(Enum(MessageType, name="message_type"), nullable=False)
    public_template = Column(Boolean, nullable=False, default=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)

    company = relationship("Company", back_populates="templates")
