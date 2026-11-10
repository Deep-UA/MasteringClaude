import allure
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
        # Step title names the email only, never the password.
        with allure.step(f"Log in via UI as {email}"):
            self.email.fill(email)
            self.password.fill(password)
            self.submit.click()
