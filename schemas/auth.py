from pydantic import BaseModel
from schemas.common.types import ClientEmail, ClientPassword


class RegisterRequest(BaseModel):
    email: ClientEmail
    password: ClientPassword

class LoginRequest(BaseModel):
    email: ClientEmail
    password: str