from pydantic import BaseModel


class Brand(BaseModel):
    id: str
    name: str
    slug: str
