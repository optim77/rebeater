import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from fastapi_pagination import Page, Params
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from starlette import status

from database import get_db
from models import Company
from models.template import Template
from utils.get_company import validate_company_access
from utils.security import get_current_user

router = APIRouter(prefix="/templates", tags=["templates"])

class CreateTemplate(BaseModel):
    name: str
    description: str | None = None
    template: str

class TemplateOut(BaseModel):
    id: uuid.UUID | None = None
    name: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    template: str | None = None

class CreateTemplateOutput(BaseModel):
    id: uuid.UUID


@router.get("/public/list", response_model=Page[TemplateOut])
async def get_public_templates(
        params: Params = Depends(),
        db: Session = Depends(get_db),
):
    templates = db.query(Template).filter_by(public=True)

    if not templates:
        raise HTTPException(status_code=404, detail="Template not found")

    return paginate(templates, params)

@router.get("/{company_id}/list", response_model=Page[TemplateOut])
async def get_templates(
        company_id: uuid.UUID,
        search_term: str = Query(None),
        params: Params = Depends(),
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):

    query = db.query(Template).filter_by(company_id=company_id).order_by(Template.created_at.desc())
    if search_term:
        query = query.filter(
            or_(
                Template.name.ilike(f"%{search_term}%"),
                Template.description.ilike(f"%{search_term}%"),
                Template.template.ilike(f"%{search_term}%"),
            )
        )

    return paginate(query, params)


@router.get("/{company_id}/{template_id}", response_model=TemplateOut)
async def get_template(
        company_id: uuid.UUID,
        template_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
    survey = db.query(Template).filter_by(id=template_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Template not found")

    return survey

@router.post("/{company_id}/create", response_model=CreateTemplateOutput)
def create_template(
        company_id: uuid.UUID,
        template: CreateTemplate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    company = (
        db.query(Company)
        .filter_by(id=company_id, owner_id=current_user.id)
        .first()
    )

    template = Template(
        name=template.name,
        description=template.description,
        template=template.template,
        company_id=company.id
    )

    db.add(template)
    db.commit()
    db.refresh(template)
    return { "id": template.id }


@router.put("/{company_id}/{template_id}/update", response_model=CreateTemplateOutput)
def update_template(
        company_id: uuid.UUID,
        template: CreateTemplate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    db_template = db.query(Template).filter_by(id=template.id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    db_template.name = template.name
    db_template.description = template.description
    db_template.template = template.template

    db.commit()
    db.refresh(db_template)

    return { "id": db_template.id }

@router.delete("/{company_id}/{template_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
        company_id: uuid.UUID,
        template_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: None = Depends(validate_company_access)
):
    template = db.query(Template).filter_by(id=template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Survey not found")

    db.delete(template)
    db.commit()

    return None