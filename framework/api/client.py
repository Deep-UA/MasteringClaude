import json

import allure
import httpx

from framework.config import Settings, get_settings


SENSITIVE_KEYS = {"password", "access_token"}


def _pretty(raw: bytes) -> str:
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except ValueError:
        return raw.decode(errors="replace")
    if isinstance(data, dict):
        data = {k: "***" if k in SENSITIVE_KEYS else v for k, v in data.items()}
    return json.dumps(data, indent=2)


def _attach_to_allure(response: httpx.Response) -> None:
    """Attach request + response to the current Allure test (no-op outside a test).

    Headers are left out on purpose: they carry the bearer token.
    """
    response.read()
    request = response.request
    allure.attach(
        f"{request.method} {request.url}\n{_pretty(request.content)}\n\n"
        f"HTTP {response.status_code}\n{_pretty(response.content)}",
        name=f"{request.method} {request.url.path} -> {response.status_code}",
        attachment_type=allure.attachment_type.TEXT,
    )


class ApiClient(httpx.Client):
    """httpx client preconfigured for the Toolshop API."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        super().__init__(
            base_url=settings.api_url,
            timeout=settings.api_timeout,
            headers={"Accept": "application/json"},
            event_hooks={"response": [_attach_to_allure]},
        )
