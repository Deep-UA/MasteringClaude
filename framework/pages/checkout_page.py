from typing import Literal

import allure
from playwright.sync_api import Page

from framework.pages.base_page import BasePage

PaymentMethod = Literal[
    "bank-transfer", "cash-on-delivery", "credit-card", "buy-now-pay-later", "gift-card"
]


class CheckoutPage(BasePage):
    """4-step wizard: cart -> sign in -> billing address -> payment."""

    path = "/checkout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Step 1: cart
        self.product_titles = page.get_by_test_id("product-title")
        self.cart_total = page.get_by_test_id("cart-total")
        self._proceed_cart = page.get_by_test_id("proceed-1")
        # Step 2: sign in ("you are already logged in" when authenticated)
        self._proceed_signed_in = page.get_by_test_id("proceed-2")
        # Step 3: billing address, prefilled from the user's profile.
        # Proceed stays disabled until street, house_number, city, state, country, postal_code are set.
        self._proceed_address = page.get_by_test_id("proceed-3")
        # Step 4: payment
        self.payment_method = page.get_by_test_id("payment-method")
        self._finish = page.get_by_test_id("finish")
        # "Payment was successful"
        self.success_message = page.get_by_test_id("payment-success-message")

    def proceed_from_cart(self) -> None:
        with allure.step("Checkout: proceed from cart"):
            self._proceed_cart.click()

    def proceed_signed_in(self) -> None:
        with allure.step("Checkout: proceed as signed-in user"):
            self._proceed_signed_in.click()

    def proceed_from_billing_address(self) -> None:
        with allure.step("Checkout: proceed from billing address"):
            self._proceed_address.click()

    def pay(self, method: PaymentMethod) -> None:
        with allure.step(f"Checkout: pay with {method}"):
            self.payment_method.select_option(method)
            self._finish.click()
