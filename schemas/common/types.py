from typing import Annotated

from pydantic import AfterValidator

from domain.validators import normalize_name, validate_phone, validate_email, validate_password, validate_portal_url, \
    validate_company_name

ClientName = Annotated[str, AfterValidator(normalize_name)]
ClientPhone = Annotated[str, AfterValidator(validate_phone)]
ClientEmail = Annotated[str, AfterValidator(validate_email)]
ClientPassword = Annotated[str, AfterValidator(validate_password)]
ClientPortalURL = Annotated[str | None, AfterValidator(validate_portal_url)]
CompanyName = Annotated[str, AfterValidator(validate_company_name)]