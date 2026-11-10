import allure
import httpx

from framework.models import LoginRequest, RegisterUser


class AuthApi:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def register(self, user: RegisterUser) -> httpx.Response:
        with allure.step(f"API: register user {user.email}"):
            # The API rejects explicit nulls (e.g. address.state) but accepts omitted fields.
            return self._client.post(
                "/users/register", json=user.model_dump(mode="json", exclude_none=True)
            )

    def login(self, email: str, password: str) -> httpx.Response:
        # Step title names the email only, never the password.
        with allure.step(f"API: log in as {email}"):
            body = LoginRequest(email=email, password=password)
            return self._client.post("/users/login", json=body.model_dump())

    def me(self, token: str) -> httpx.Response:
        with allure.step("API: get current user"):
            return self._client.get(
                "/users/me", headers={"Authorization": f"Bearer {token}"}
            )

    def delete_user(self, user_id: str, admin_token: str) -> httpx.Response:
        # Requires the admin role.
        with allure.step(f"API: delete user {user_id}"):
            return self._client.delete(
                f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"}
            )
