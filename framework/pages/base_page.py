from typing import Self

from playwright.sync_api import Page

from framework.pages.components.header import Header


class BasePage:
    """Common page behaviour. `path` is relative to the `base_url` fixture."""

    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)

    def open(self) -> Self:
        self.page.goto(self.path)
        return self
