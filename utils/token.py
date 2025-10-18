from jose import jwt
from datetime import datetime, timedelta

from config import JWT_SECRET


def create_token(data: dict, expires_in: int = 60*24):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
