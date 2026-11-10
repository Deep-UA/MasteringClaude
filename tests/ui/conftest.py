import json

import pytest
from playwright.sync_api import Page, Playwright

from framework.config import Settings
from framework.pages import AccountPage, CheckoutPage, HomePage, LoginPage, ProductPage


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Overrides pytest-base-url so the URL comes from Settings only."""
    return settings.base_url


@pytest.fixture(scope="session", autouse=True)
def _data_test_id(playwright: Playwright) -> None:
    """Make page.get_by_test_id() target the app's `data-test` attributes.

    Lives in tests/ui so API-only runs don't start Playwright.
    """
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def logged_in_page(page: Page, auth_token: str) -> Page:
    """Page already authenticated as `test_user`, without going through the login form.

    The app keeps its JWT in localStorage['auth-token']; the init script sets it before
    any app code runs. The token expires after 300 s, which is longer than one test.
    """
    page.add_init_script(
        f"window.localStorage.setItem('auth-token', {json.dumps(auth_token)})"
    )
    return page


@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def product_page(page: Page) -> ProductPage:
    return ProductPage(page)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def account_page(page: Page) -> AccountPage:
    return AccountPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)
