from pydantic import BaseModel
from schemas.common.types import ClientName, ClientEmail, ClientPhone
import uuid
class CreateClient(BaseModel):
    name: ClientName
    email: ClientEmail
    phone: ClientPhone

class UpdateClient(BaseModel):
    name: ClientName | None = None
    email: ClientEmail | None = None
    phone: ClientPhone | None = None

class ClientOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: str

    class Config:
        from_attributes = True