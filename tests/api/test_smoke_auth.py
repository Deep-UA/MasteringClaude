import uuid

import pytest

from framework.api import AuthApi
from framework.models import LoginResponse, RegisterUser, User

pytestmark = [pytest.mark.smoke, pytest.mark.api]


def test_login(auth_api: AuthApi, test_user: RegisterUser) -> None:
    """A5: POST /users/login with the registered test user returns a bearer token."""
    response = auth_api.login(test_user.email, test_user.password)

    assert response.status_code == 200
    token = LoginResponse.model_validate(response.json())
    assert token.access_token
    assert token.token_type == "bearer"


def test_current_user(
    auth_api: AuthApi, auth_token: str, test_user: RegisterUser
) -> None:
    """A6: GET /users/me accepts the token and returns the test user's profile."""
    response = auth_api.me(auth_token)

    assert response.status_code == 200
    assert User.model_validate(response.json()).email == test_user.email


def test_login_unknown_user_rejected(auth_api: AuthApi) -> None:
    """A7: login with a random non-existent email is rejected.

    Never use a real account here: failed logins lock it for everyone.
    """
    response = auth_api.login(
        f"nobody+{uuid.uuid4().hex}@example.com", "Wrong1!password"
    )

    assert response.status_code == 401
