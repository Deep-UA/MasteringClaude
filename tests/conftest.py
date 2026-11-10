import uuid
import warnings
from collections.abc import Iterator
from datetime import date

import pytest

from framework.api import ApiClient, AuthApi, ProductsApi
from framework.config import Settings, get_settings
from framework.models import Address, LoginResponse, RegisterUser, User


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def api_client(settings: Settings) -> Iterator[ApiClient]:
    with ApiClient(settings) as client:
        yield client


@pytest.fixture(scope="session")
def auth_api(api_client: ApiClient) -> AuthApi:
    return AuthApi(api_client)


@pytest.fixture(scope="session")
def products_api(api_client: ApiClient) -> ProductsApi:
    return ProductsApi(api_client)


def _delete_user(auth_api: AuthApi, settings: Settings, user_id: str) -> None:
    """Best-effort cleanup: warn instead of failing, since the shared admin account can be locked."""
    if not (settings.admin_email and settings.admin_password):
        warnings.warn(f"ADMIN_EMAIL/ADMIN_PASSWORD not set; test user {user_id} was not deleted", stacklevel=1)
        return
    login = auth_api.login(settings.admin_email, settings.admin_password.get_secret_value())
    if login.status_code != 200:
        warnings.warn(f"Admin login failed ({login.status_code}); test user {user_id} was not deleted", stacklevel=1)
        return
    token = LoginResponse.model_validate(login.json()).access_token
    response = auth_api.delete_user(user_id, token)
    if response.status_code != 204:
        warnings.warn(f"Deleting test user {user_id} failed ({response.status_code}): {response.text}", stacklevel=1)


@pytest.fixture(scope="session")
def test_user(auth_api: AuthApi, settings: Settings) -> Iterator[RegisterUser]:
    """A fresh user registered once per session (= once per xdist worker), deleted afterwards.

    Avoids the shared demo accounts, which other people can lock. Shared by every test in
    the worker, so tests must not change it (password, profile, failed logins).
    """
    suffix = uuid.uuid4().hex[:12]
    user = RegisterUser(
        first_name="Qa",
        last_name="Bot",
        email=f"qa+{suffix}@example.com",
        password=f"Qa1!{suffix}",  # upper + lower + digit + symbol, >= 8 chars
        dob=date(1990, 1, 1),
        phone="0612345678",
        address=Address(street="Main Street 1", city="Utrecht", country="NL"),
    )
    response = auth_api.register(user)
    assert response.status_code == 201, f"Test user registration failed: {response.text}"
    user_id = User.model_validate(response.json()).id
    yield user
    _delete_user(auth_api, settings, user_id)


@pytest.fixture
def auth_token(auth_api: AuthApi, test_user: RegisterUser) -> str:
    """Fresh access token per test (tokens expire after 300 s)."""
    response = auth_api.login(test_user.email, test_user.password)
    assert response.status_code == 200, f"Test user login failed: {response.text}"
    return LoginResponse.model_validate(response.json()).access_token
