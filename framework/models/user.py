from datetime import date, datetime

from pydantic import BaseModel, Field


class Address(BaseModel):
    street: str
    house_number: str | None = None
    city: str
    state: str | None = None
    country: str
    postal_code: str | None = None


class RegisterUser(BaseModel):
    """Request body for POST /users/register. Send with `model_dump(mode="json")`."""

    first_name: str
    last_name: str
    email: str
    # rules: >= 8 chars, upper + lower + digit + symbol.
    # repr=False keeps it out of tracebacks, which pytest/Allure show on failure.
    password: str = Field(repr=False)
    dob: date  # must be 18..75 years ago
    phone: str
    address: Address


class User(BaseModel):
    """Response of POST /users/register and GET /users/me."""

    id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    dob: date
    address: Address
    created_at: datetime
