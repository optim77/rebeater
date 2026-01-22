from pydantic import BaseModel
from schemas.common.types import ClientPortalURL, CompanyName
from uuid import UUID

class GroupCreate(BaseModel):
    name: CompanyName
    description: ClientPortalURL
    google_review_link: ClientPortalURL
    facebook_url: ClientPortalURL
    instagram_link: ClientPortalURL
    linkedin_link: ClientPortalURL
    tiktok_link: ClientPortalURL
    znany_lekarz: ClientPortalURL
    booksy_link: ClientPortalURL


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class GroupOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    owner_id: UUID
    google_review_link: str | None = None
    facebook_url: str | None = None
    instagram_link: str | None = None
    linkedin_link: str | None = None
    tiktok_link: str | None = None
    znany_lekarz: str | None = None
    booksy_link: str | None = None

    model_config = {
        "from_attributes": True
    }
