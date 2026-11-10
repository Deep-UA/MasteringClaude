from playwright.sync_api import Page

from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/auth/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.email = page.get_by_test_id("email")
        self.password = page.get_by_test_id("password")
        self.submit = page.get_by_test_id("login-submit")
        self.error = page.get_by_test_id("login-error")

    def login(self, email: str, password: str) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.submit.click()
