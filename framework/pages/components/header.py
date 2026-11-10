import allure
from playwright.sync_api import Page


class Header:
    """Top navigation bar, shared by every page."""

    def __init__(self, page: Page) -> None:
        self.sign_in = page.get_by_test_id("nav-sign-in")
        # Shows "<first> <last>" when logged in.
        self.user_menu = page.get_by_test_id("nav-menu")
        # Only rendered when the cart is not empty.
        self.cart = page.get_by_test_id("nav-cart")
        self.cart_quantity = page.get_by_test_id("cart-quantity")

    def open_cart(self) -> None:
        with allure.step("Open cart"):
            self.cart.click()
