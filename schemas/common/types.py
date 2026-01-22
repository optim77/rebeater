from typing import Annotated

from pydantic import AfterValidator, StringConstraints

from domain.validators import normalize_name, validate_phone, validate_email, validate_password, validate_portal_url, \
    validate_company_name, normalize_text

ClientName = Annotated[
    str,
    StringConstraints(max_length=255),
    AfterValidator(normalize_name)
]

ClientPhone = Annotated[
    str,
    StringConstraints(max_length=20),
    AfterValidator(validate_phone)
]

ClientEmail = Annotated[
    str,
    StringConstraints(max_length=255),
    AfterValidator(validate_email)
]

ClientPassword = Annotated[
    str,
    StringConstraints(max_length=100),
    AfterValidator(validate_password)
]

ClientPortalURL = Annotated[
    str | None,
    StringConstraints(max_length=255),
    AfterValidator(validate_portal_url)
]

CompanyName = Annotated[
    str,
    StringConstraints(max_length=255),
    AfterValidator(validate_company_name)
]

TextField = Annotated[
    str,
    StringConstraints(max_length=1000),
    AfterValidator(normalize_text)
]