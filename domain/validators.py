import re

EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

PASSWORD_REGEX = re.compile(
    r"A-Za-z0-9@#$%^&+=]{8,}"
)
# TODO: Delete in prod
PASSWORD_REGEX = re.compile(
    r"A-Za-z0-9"
)

COMPANY_REGEX = re.compile(
    r"^[A-Za-z0-9._%+/-]"
)

def normalize_name(value: str) -> str:
    return value.strip()

def validate_phone(value: str) -> str:
    if not re.fullmatch(r"\+?[0-9]{9,15}", value):
        raise ValueError("Phone number must be 9 digits only")
    return value


def validate_email(value: str) -> str:
    value = value.strip().lower()

    if not EMAIL_REGEX.fullmatch(value):
        raise ValueError("Invalid email address")

    return value


def validate_password(value: str) -> str:
    if not PASSWORD_REGEX.fullmatch(value):
        raise ValueError("Password must be 8 characters long")
    return value

def validate_portal_url(value: str) -> str:
    return value.strip()

def validate_company_name(value: str) -> str:
    if not COMPANY_REGEX.fullmatch(value):
        raise ValueError("Company name includes forbidden characters")
    return value