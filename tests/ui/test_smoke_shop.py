import re

import pytest
from playwright.sync_api import Page, expect

from framework.models import Product
from framework.pages import HomePage, ProductPage

pytestmark = [pytest.mark.smoke, pytest.mark.ui]


def test_home_page_loads(page: Page, home_page: HomePage) -> None:
    """U1: the home page renders the product grid."""
    home_page.open()

    expect(page).to_have_title(re.compile("Toolshop"))
    expect(home_page.product_cards).to_have_count(9)


def test_search(home_page: HomePage) -> None:
    """U2: searching narrows the grid to matching products."""
    home_page.open()
    home_page.search("pliers")

    expect(home_page.search_caption).to_contain_text("pliers")
    expect(home_page.product_names.first).to_be_visible()
    names = home_page.product_names.all_inner_texts()
    assert all("pliers" in name.lower() for name in names), names


def test_product_details(page: Page, home_page: HomePage) -> None:
    """U3: a product card opens its detail page."""
    home_page.open()
    product = home_page.open_product(0)

    expect(page).to_have_url(re.compile(r"/product/"))
    expect(product.name).to_be_visible()
    expect(product.unit_price).to_be_visible()


def test_add_to_cart(product_page: ProductPage, in_stock_product: Product) -> None:
    """U4: adding a product updates the cart badge."""
    product_page.open_product(in_stock_product.id)
    product_page.add_to_cart()

    expect(product_page.header.cart_quantity).to_have_text("1")
