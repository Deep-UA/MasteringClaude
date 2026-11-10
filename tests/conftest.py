import uuid
from collections.abc import Iterator
from datetime import date

import pytest

from framework.api import ApiClient, AuthApi, ProductsApi
from framework.config import Settings, get_settings
from framework.models import Address, LoginResponse, RegisterUser


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


@pytest.fixture(scope="session")
def test_user(auth_api: AuthApi) -> RegisterUser:
    """A fresh user registered once per session (= once per xdist worker).

    Avoids the shared demo accounts, which other people can lock.
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
    return user


@pytest.fixture
def auth_token(auth_api: AuthApi, test_user: RegisterUser) -> str:
    """Fresh access token per test (tokens expire after 300 s)."""
    response = auth_api.login(test_user.email, test_user.password)
    assert response.status_code == 200, f"Test user login failed: {response.text}"
    return LoginResponse.model_validate(response.json()).access_token
