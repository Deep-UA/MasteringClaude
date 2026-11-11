import pytest
from playwright.sync_api import Page, expect

from framework.models import Product
from framework.pages import CheckoutPage, ProductPage

pytestmark = [pytest.mark.smoke, pytest.mark.ui]


def test_checkout_cash_on_delivery(
    logged_in_page: Page,
    product_page: ProductPage,
    checkout_page: CheckoutPage,
    in_stock_product: Product,
) -> None:
    """U7: a logged-in user buys a product end to end."""
    product_page.open_product(in_stock_product.id)
    product_page.add_to_cart()
    expect(product_page.header.cart_quantity).to_have_text("1")

    product_page.header.open_cart()
    expect(checkout_page.product_titles).to_have_count(1)
    checkout_page.proceed_from_cart()
    checkout_page.proceed_signed_in()
    checkout_page.proceed_from_billing_address()
    checkout_page.pay("cash-on-delivery")

    expect(checkout_page.success_message).to_have_text("Payment was successful")
