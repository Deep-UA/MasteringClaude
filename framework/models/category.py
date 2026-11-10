from pydantic import BaseModel


class Category(BaseModel):
    """Node of GET /categories/tree (recursive)."""

    id: str
    name: str
    slug: str
    parent_id: str | None
    sub_categories: list["Category"] = []
