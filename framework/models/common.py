from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    """Laravel-style paginated list, e.g. GET /products."""

    current_page: int
    last_page: int
    per_page: int
    total: int
    data: list[T]
