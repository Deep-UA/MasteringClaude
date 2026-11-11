# Toolshop Test Automation

UI + API test framework for the public demo shop [Practice Software Testing – Toolshop](https://practicesoftwaretesting.com)
and its REST API (`https://api.practicesoftwaretesting.com`).

**Stack:** uv · pytest · pytest-playwright · pydantic v2 / pydantic-settings · httpx · pytest-xdist · allure-pytest

Design decisions and the smoke suite plan: [`documents/test-automation-plan.md`](documents/test-automation-plan.md).

## Setup

Requirements: [uv](https://docs.astral.sh/uv/), and Java + [Allure CLI](https://allurereport.org/docs/install/) for viewing reports.

```bash
uv sync                                 # create .venv and install dependencies from uv.lock
uv run playwright install chromium      # download the browser
cp .env.example .env                    # optional: defaults already point at the public demo
```

## Running tests

```bash
uv run pytest -m smoke -n auto          # smoke suite, in parallel (one worker per CPU)
uv run pytest -m api                    # API tests only (no browser is started)
uv run pytest -m ui                     # UI tests only
uv run pytest tests/ui/test_x.py -k name --headed   # one test, visible browser
```

Markers: `smoke`, `ui`, `api` (unknown markers fail the run: `--strict-markers`).
`-n auto` is deliberately not in `addopts`, so a single test runs in one process and is easy to debug.

## Reports

Every run writes raw results to `allure-results/`. They accumulate across runs, so delete the folder first
if you want a report of one run only.

```bash
rm -rf allure-results && uv run pytest -m smoke -n auto
allure serve allure-results                                         # build + open in the browser
allure generate allure-results --clean --single-file -o allure-report   # one self-contained index.html
```

The report contains:
- steps for every page-object action and API call, each API step with its request/response attached;
- on a failed UI test: screenshot and Playwright trace (open a trace with `uv run playwright show-trace <file>.zip`);
- environment info (base URL, API URL, browser, Python version).

Screenshots and traces of failed tests are also kept in `test-results/`.

## Configuration

Settings are read from environment variables, then `.env`, then defaults (`framework/config.py`).

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | `https://practicesoftwaretesting.com` | Web app under test |
| `API_URL` | `https://api.practicesoftwaretesting.com` | REST API under test |
| `API_TIMEOUT` | `10` | httpx timeout in seconds |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | unset | Optional: admin login used to delete the test users after the run. Unset → cleanup is skipped with a warning |

No credentials are needed to run tests: each run registers its own user (see below).

## Project structure

```
framework/
  config.py          typed settings (pydantic-settings)
  api/               ApiClient (httpx) + AuthApi, ProductsApi wrappers
  models/            pydantic models for API requests/responses
  pages/             page objects (+ components/header.py)
tests/
  conftest.py        settings, API fixtures, test_user, auth_token, in_stock_product, Allure environment
  ui/conftest.py     base_url, data-test locators, page-object fixtures, logged_in_page, failure artifacts
.github/workflows/smoke.yml   CI: smoke suite + Allure report artifact
```

## Conventions

- **Locators:** use the app's `data-test` attributes via `page.get_by_test_id(...)`.
- **Page objects** perform actions and expose locators; assertions (`expect(...)`) stay in the tests.
- **API wrappers** return the raw `httpx.Response`; tests check the status and validate the body with a model,
  e.g. `Paginated[Product].model_validate(response.json())`.
- **Test user:** `test_user` is registered once per session (one per xdist worker), so tests never depend on the
  shared demo accounts, which other people can lock. Tests must not change this user (password, profile).
- **Logged-in UI tests:** use `logged_in_page` (token injected into `localStorage`) instead of the login form,
  unless the login form itself is under test.
- **Test data:** never hard-code product IDs; the demo database is reset periodically and IDs change.
  Use `in_stock_product` or look data up through the API.

## CI

`.github/workflows/smoke.yml` runs on push to `main`, on pull requests and manually: installs with
`uv sync --locked`, runs `pytest -m "smoke and ui" -n auto`, and uploads
- `allure-report` — single-file report, every run;
- `playwright-traces` — `test-results/`, only when tests fail.

Optional repository secrets `ADMIN_EMAIL` / `ADMIN_PASSWORD` enable test-user cleanup.

## Known limitations

- **UI tests in CI may be blocked:** the demo site's Cloudflare bot check has blocked the browser on GitHub-hosted
  runners (the page stays on "Just a moment..."). CI runs the UI smoke tests; API smoke tests run locally
  (`uv run pytest -m "smoke and api"`). Planned fix: start the open-source app in CI and point `BASE_URL`/`API_URL` at it.
- **Shared public demo:** the database is reset periodically (product IDs change, registered users are removed)
  and the API sometimes answers slowly or with 500s. A run that overlaps a reset or an outage can fail.
- **Sessions last 5 minutes:** API and web tokens expire after 300 s and are not refreshed; keep tests short.
- **Secrets in artifacts (accepted):** Playwright traces of failed UI tests contain the typed test-user password
  and login request bodies, and a failing test that uses `auth_token` shows the token in its traceback.
  This only exposes disposable per-run accounts. Do not point the suite at real accounts without revisiting this.
- **Payments:** `CheckoutPage.pay()` supports `cash-on-delivery` only; the other methods need extra fields.
