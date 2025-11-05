import uuid

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from fastapi_pagination import Page, Params
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from starlette import status
from fastapi_pagination.ext.sqlalchemy import paginate
from database import get_db
from models.company import Company
from models.template import Template
from models.utils.messageType import MessageType

router = APIRouter(prefix="/templates", tags=["templates"])

class CreateTemplate(BaseModel):
    name: str
    message: str
    messageType: MessageType

class MessageOut(BaseModel):
    name: str
    message: str
    type: MessageType
    company_id: uuid.UUID

@router.get("/{company_id}/templates", response_model=Page[MessageOut])
async def get_templates(
        company_id: str,
        search_term: str = Query(None),
        params: Params = Depends(),
        current_user = Depends(current_user),
        db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id,Company.owner_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    query = db.query(Template).filter(Template.company_id == company_id)
    if search_term:
        query = query.filter(
            or_(
                Template.name.ilike(f"%{search_term}%"),
                Template.message.ilike(f"%{search_term}%"),
                Template.type.ilike(f"%{search_term}%"),
            )
        )

    return paginate(query, params)

@router.post("/templates")
def create_template(template: CreateTemplate):
    pass