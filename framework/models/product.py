from typing import Literal

from pydantic import BaseModel


class ProductImage(BaseModel):
    id: str
    file_name: str
    title: str


class ProductCategory(BaseModel):
    id: str
    name: str
    slug: str


class ProductBrand(BaseModel):
    id: str
    name: str


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    in_stock: bool
    is_rental: bool
    is_location_offer: bool
    is_eco_friendly: bool
    co2_rating: Literal["A", "B", "C", "D", "E"]
    product_image: ProductImage
    category: ProductCategory
    brand: ProductBrand
