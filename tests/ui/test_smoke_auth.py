import re

import pytest
from playwright.sync_api import Page, expect

from framework.models import RegisterUser
from framework.pages import AccountPage, HomePage, LoginPage

pytestmark = [pytest.mark.smoke, pytest.mark.ui]


def test_login_via_form(
    page: Page,
    login_page: LoginPage,
    account_page: AccountPage,
    test_user: RegisterUser,
) -> None:
    """U5: logging in through the form lands on the account page."""
    login_page.open().login(test_user.email, test_user.password)

    expect(page).to_have_url(re.compile(r"/account$"))
    expect(account_page.title).to_have_text("My account")


def test_login_via_token(
    logged_in_page: Page, home_page: HomePage, test_user: RegisterUser
) -> None:
    """U6: an API token injected into the browser logs the user in (used by other UI tests)."""
    home_page.open()

    expect(home_page.header.user_menu).to_have_text(
        f"{test_user.first_name} {test_user.last_name}"
    )
    expect(home_page.header.sign_in).to_be_hidden()
