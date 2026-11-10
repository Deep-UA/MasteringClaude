from typing import Self

import allure
from playwright.sync_api import Page

from framework.pages.base_page import BasePage


class ProductPage(BasePage):
    path = "/product/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name = page.get_by_test_id("product-name")
        self.unit_price = page.get_by_test_id("unit-price")
        self.quantity = page.get_by_test_id("quantity")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")

    def open_product(self, product_id: str) -> Self:
        with allure.step(f"Open product {product_id}"):
            self.page.goto(f"{self.path}{product_id}")
        return self

    def add_to_cart(self) -> None:
        with allure.step("Add product to cart"):
            self.add_to_cart_button.click()
