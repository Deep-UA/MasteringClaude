import pytest
from pydantic import TypeAdapter

from framework.api import ProductsApi
from framework.models import Brand, Category, Paginated, Product

pytestmark = [pytest.mark.smoke, pytest.mark.api]


def test_products_list(products_api: ProductsApi) -> None:
    """A1: GET /products returns a valid, non-empty page."""
    response = products_api.list_products()

    assert response.status_code == 200
    page = Paginated[Product].model_validate(response.json())
    assert page.total > 0
    assert 0 < len(page.data) <= page.per_page


def test_product_by_id(products_api: ProductsApi, in_stock_product: Product) -> None:
    """A2: GET /products/{id} returns the product taken from the list."""
    response = products_api.get_product(in_stock_product.id)

    assert response.status_code == 200
    product = Product.model_validate(response.json())
    assert product.id == in_stock_product.id
    assert product.price > 0


def test_categories_tree(products_api: ProductsApi) -> None:
    """A3: GET /categories/tree returns a non-empty tree."""
    response = products_api.categories_tree()

    assert response.status_code == 200
    categories = TypeAdapter(list[Category]).validate_python(response.json())
    assert categories


def test_brands(products_api: ProductsApi) -> None:
    """A4: GET /brands returns a non-empty list."""
    response = products_api.brands()

    assert response.status_code == 200
    brands = TypeAdapter(list[Brand]).validate_python(response.json())
    assert brands
