from uuid import UUID

from fastapi import HTTPException
from fastapi.params import Depends

from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.company import Company
from utils.security import get_current_user


def get_company(
        company_id: UUID,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
) -> Company | None:
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


def validate_company_access(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> None:
    company_exists = db.query(Company).filter(
        Company.id == company_id,
        Company.owner_id == current_user.id
    ).first()

    if not company_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )