from pydantic import BaseModel
from schemas.common.types import ClientName, ClientEmail, ClientPhone
import uuid
class CreateClient(BaseModel):
    name: ClientName
    surname: ClientName
    email: ClientEmail
    phone: ClientPhone

class UpdateClient(BaseModel):
    name: ClientName | None = None
    surname: ClientName | None = None
    email: ClientEmail | None = None
    phone: ClientPhone | None = None

class ClientOut(BaseModel):
    id: uuid.UUID
    name: str | None = None
    surname: str | None = None
    email: str
    phone: str | None

    class Config:
        from_attributes = True