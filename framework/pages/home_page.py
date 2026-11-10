import re

from playwright.sync_api import Page

from framework.pages.base_page import BasePage
from framework.pages.product_page import ProductPage


class HomePage(BasePage):
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Cards are `product-<26-char ULID>`; the regex excludes product-name/product-price.
        self.product_cards = page.get_by_test_id(re.compile(r"^product-[0-9A-Z]{26}$"))
        self.product_names = page.get_by_test_id("product-name")
        self.search_input = page.get_by_test_id("search-query")
        self.search_button = page.get_by_test_id("search-submit")
        self.search_caption = page.get_by_test_id(
            "search-caption"
        )  # "Searched for: <term>"
        self._search_completed = page.get_by_test_id("search_completed")

    def search(self, term: str) -> None:
        self.search_input.fill(term)
        self.search_button.click()
        self._search_completed.wait_for()  # results grid re-rendered for the new term

    def open_product(self, index: int = 0) -> ProductPage:
        self.product_cards.nth(index).click()
        return ProductPage(self.page)
