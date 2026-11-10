import pytest
from playwright.sync_api import Playwright

from framework.config import Settings


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
