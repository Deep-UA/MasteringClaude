# Toolshop Test Automation — Framework Skeleton & Smoke Suite Plan

> Scope: **plan only** — nothing is built until approved.

## 1. Context

We are starting a test automation project for **Practice Software Testing – Toolshop** (`https://practicesoftwaretesting.com`, Angular 20 SPA, v5.0) and its REST API (`https://api.practicesoftwaretesting.com`).
Goal: a clean, scalable Python framework skeleton + a fast **smoke suite (UI + API)** that runs in parallel, produces an Allure report, and runs on GitHub Actions.

**Stack:** uv · pytest · pytest-playwright · pydantic v2 (+ pydantic-settings) · httpx · pytest-xdist · allure-pytest
**Decisions (confirmed):** build in this repo (`MasteringClaude`) · smoke = UI + API · Chromium + GitHub Actions · tests use a **fresh user registered per test session** (not the shared demo account).

## 2. Exploration findings (via `playwright-cli`)

| Area | Finding | Impact on framework |
|---|---|---|
| Locators | App exposes stable `data-test` attributes everywhere (`nav-sign-in`, `search-query`, `search-submit`, `add-to-cart`, `cart-quantity`, `proceed-1`, `finish`, `product-<id>`, …) | Configure `selectors.set_test_id_attribute("data-test")` → use `page.get_by_test_id()` |
| Home `/` | Product grid (9/page, 6 pages, 50 products), sort combobox, price slider, search, category/brand/eco filters, pagination | Home page object + search smoke |
| Product `/product/{id}` | `product-name`, `unit-price`, `quantity`, `increase/decrease-quantity`, `add-to-cart`, `add-to-favorites`; toast "Product added to shopping cart." | Product page object |
| Login `/auth/login` | `email`, `password`, `login-submit`; success → `/account`, `page-title` = "My account", `nav-menu` shows user | Login page object + smoke |
| Register `/auth/register` | Full form (`first-name`, `dob`, `country`, `postal_code`, …) | Not in smoke (later regression) |
| Contact `/contact` | `first-name`, `last-name`, `email`, `subject`, `message`, `attachment`, `contact-submit` | Not in smoke (later) |
| Checkout `/checkout` | 4-step wizard: cart (`proceed-1`) → sign-in / guest → billing address (`proceed-3`) → payment (`payment-method`: bank-transfer, cash-on-delivery, credit-card, buy-now-pay-later, gift-card; `finish`) | Checkout page object, E2E smoke |
| State | Cart in **sessionStorage** (`cart_id`, `cart_quantity`); auth JWT in **localStorage** (`auth-token`) | Can inject API token into the browser → fast logged-in UI tests |
| API | `POST /users/login` → `access_token` (JWT, **TTL 300 s**); `GET /products` (paginated: `current_page,last_page,per_page,total,data[]`), `/products/{id}`, `/categories/tree`, `/brands`, `/users/me`; Swagger at `/api/documentation` | httpx client + pydantic models; token fixture must be refreshed (short TTL) |
| Demo users | `customer@practicesoftwaretesting.com` / `welcome01` exists, but was later found **locked** ("too many failed attempts", HTTP 423) by other people using the shared demo; other demo logins returned 500 | Do not depend on shared accounts → register a fresh user per session via `POST /users/register` |
| Registration | `POST /users/register` → 201 + user; password ≥ 8 chars with upper/lower/digit/symbol; `dob` 18–75 years ago; nested `address` | `RegisterUser` request model; session fixture creates `qa+<uuid>@example.com` and deletes it afterwards (`DELETE /users/{id}` needs the **admin** role) |
| Risks | Shared public demo: **DB is reset periodically (IDs change)**, accounts can be locked by others, other users write invoices; console errors on load; intermittent 500s; possible rate limiting | Assert on structure/behaviour not exact catalog data; resolve product IDs dynamically via API; never send failed logins to a real account |

## 3. Target project structure

```
MasteringClaude/
├── pyproject.toml            # uv project, deps, pytest config, markers
├── uv.lock
├── .env.example              # BASE_URL, API_URL, API_TIMEOUT
├── .gitignore                # .env, allure-results/, test-results/, .venv
├── documents/
│   └── test-automation-plan.md
├── framework/
│   ├── config.py             # pydantic-settings Settings (env-driven)
│   ├── api/
│   │   ├── client.py         # thin httpx.Client wrapper (base_url, auth, allure attach)
│   │   ├── auth_api.py
│   │   └── products_api.py   # products, categories, brands
│   ├── models/               # pydantic v2 response models
│   │   ├── common.py         # Paginated[T] generic
│   │   ├── product.py, category.py, brand.py
│   │   └── auth.py, user.py
│   ├── pages/                # Page Objects (get_by_test_id)
│   │   ├── base_page.py
│   │   ├── components/header.py
│   │   ├── home_page.py, product_page.py, login_page.py
│   │   └── cart_page.py / checkout_page.py
│   └── utils/allure_helpers.py
├── tests/
│   ├── conftest.py           # settings, test-id attr, allure env, screenshots on failure
│   ├── api/conftest.py       # api_client, auth_token fixtures
│   ├── api/test_smoke_*.py
│   ├── ui/conftest.py        # page objects, logged_in_page (token injection)
│   └── ui/test_smoke_*.py
└── .github/workflows/smoke.yml
```

## 4. Framework skeleton build plan

| # | Step | What | Why | How |
|---|---|---|---|---|
| 1 | Init project | Clean up PyCharm stub, set up uv project | Single reproducible env + lockfile | Remove `main.py`; `uv add --dev pytest pytest-playwright pytest-xdist allure-pytest httpx pydantic pydantic-settings`; `uv run playwright install chromium` |
| 2 | Config | `framework/config.py` with `Settings(BaseSettings)` | One typed source for URLs/timeouts; env-overridable in CI | pydantic-settings reading `.env` + env vars; `@lru_cache get_settings()`; commit `.env.example` only |
| 3 | pytest config | `[tool.pytest.ini_options]` in `pyproject.toml` | Consistent runs locally and in CI | `testpaths=tests`, markers `smoke/ui/api`, `addopts = --base-url … --browser chromium --alluredir=allure-results --screenshot=only-on-failure --tracing=retain-on-failure`, `strict-markers` |
| 4 | Pydantic models | Models for Product, Category (tree, recursive), Brand, LoginRequest/LoginResponse, RegisterUser, User, `Paginated[T]` | Schema validation = contract check for free; typed data in tests | `BaseModel` with `model_config = ConfigDict(extra="ignore")`; generic `Paginated[Product]` |
| 5 | API client | `ApiClient` over `httpx.Client` + domain wrappers (`AuthApi`, `ProductsApi`) | Reusable, readable API calls; single place for base URL/headers/logging | Methods return raw `httpx.Response`; tests parse via `Model.model_validate(resp.json())`; event hook attaches request/response to Allure |
| 6 | API fixtures | `api_client` (session), `test_user` (session: registered once per run / per xdist worker), `auth_token` (function: fresh login) | Isolation from shared demo accounts; JWT TTL is 300 s | `tests/conftest.py`; `test_user` registers `qa+<uuid>@example.com` via `/users/register`, is read-only for tests, and in teardown is deleted with the admin login from `ADMIN_EMAIL`/`ADMIN_PASSWORD` (best-effort: warns if unset or the shared admin is locked); `auth_token` logs it in via `/users/login` |
| 7 | Locator strategy | `data-test` as test-id attribute | Stable, intent-revealing locators | Session fixture: `playwright.selectors.set_test_id_attribute("data-test")` |
| 8 | Page Objects | `BasePage` (+`Header` component), Home, Product, Login, Checkout | Encapsulate UI; tests read as business steps | Constructor takes `Page`; methods like `open()`, `search(term)`, `add_to_cart()`; assertions in tests via `expect` |
| 9 | UI fixtures | Page-object fixtures, `logged_in_page` | Fast authenticated tests without UI login each time | Get token via API → `page.add_init_script` to set `localStorage['auth-token']` before navigation |
| 10 | Test data | Product lookup via API (e.g. first in-stock product) | Shared demo data changes; avoid hard-coded IDs | Fixture `in_stock_product` using `ProductsApi` |
| 11 | Allure integration | Steps, attachments, environment info | Readable reporting for UI + API | `allure.step` in page objects/clients; screenshot + trace on failure hook; `environment.properties` written at session start |
| 12 | Parallelism | pytest-xdist | Fast smoke | `uv run pytest -m smoke -n auto`; fixtures xdist-safe (no shared mutable state; each test own browser context) |
| 13 | CI | `.github/workflows/smoke.yml` | Automated smoke on push/PR + report artifact | `astral-sh/setup-uv` → `uv sync` → `uv run playwright install --with-deps chromium` → `pytest -m smoke -n auto` → generate Allure HTML (allure CLI action) → upload artifact; no secrets needed (users are registered per run) |
| 14 | Docs | README section: setup, run, report | Onboarding | Commands: `uv sync`, `uv run pytest -m smoke -n auto`, `allure serve allure-results` |

## 5. Smoke test suite

All tests marked `@pytest.mark.smoke` + `ui`/`api`. Target: whole suite < 2 min with `-n auto`.

### API smoke (`tests/api/`)

| # | Step | What | Why | How |
|---|---|---|---|---|
| A1 | Products list | `GET /products` returns 200 + valid page | Core catalog endpoint alive & contract intact | `Paginated[Product].model_validate`; assert `total > 0`, `len(data) <= per_page` |
| A2 | Product by id | `GET /products/{id}` for id from A1 list | Detail endpoint works | Model validate; `id` matches; `price > 0` |
| A3 | Categories tree | `GET /categories/tree` | Navigation/filter data present | Recursive `Category` model; non-empty list |
| A4 | Brands | `GET /brands` | Filter data present | `list[Brand]` validate; non-empty |
| A5 | Login | `POST /users/login` with the registered `test_user` → token | Auth service alive | `LoginResponse` model; `access_token` non-empty, `token_type == "bearer"` |
| A6 | Current user | `GET /users/me` with token | Token is accepted, user profile served | `User` model; `email == test_user.email` |
| A7 | Negative login | `POST /users/login` with a random **non-existent** email → 401 | Auth rejects bad creds, without locking any real account | Assert status 401 (verified: `{"error":"Unauthorized"}`) |

### UI smoke (`tests/ui/`)

| # | Step | What | Why | How |
|---|---|---|---|---|
| U1 | Home loads | Open `/`, products grid visible | App up, catalog renders | `HomePage.open()`; `expect(product cards).to_have_count(9)`; title contains "Toolshop" |
| U2 | Search | Search "pliers" → results all contain term | Search + listing works | `search-query` fill, `search-submit`; each `product-name` contains "pliers" (case-insensitive) |
| U3 | Product details | Open product from grid → details shown | Navigation & detail page work | Click first card; `expect product-name/unit-price` visible; URL matches `/product/` |
| U4 | Add to cart | Add product → toast + `cart-quantity` = 1 | Cart works | `ProductPage.add_to_cart()`; `expect(cart-quantity).to_have_text("1")` |
| U5 | UI login | Login with the registered `test_user` → `/account`, "My account" | Auth via UI works | `LoginPage.login(email, pwd)`; `expect(page).to_have_url(/account)`; `page-title` text |
| U6 | Token login | Injected API token → user menu visible | Validates fast-auth fixture used by other tests | `logged_in_page` fixture; `nav-menu` visible |
| U7 | Checkout E2E | Logged in: add product → cart → proceed → address → payment "Cash on Delivery" → finish → success message | Critical business path end-to-end | `CheckoutPage` steps: `proceed-1`, (already signed in) proceed, fill billing if empty, `proceed-3`, select `cash-on-delivery`, `finish`; assert success text "Payment was successful" |

## 6. Verification (after build)

1. `uv sync` and `uv run playwright install chromium` succeed.
2. `uv run pytest -m smoke -n auto` → all 14 tests pass locally.
3. `uv run pytest -m api` / `-m ui` run independently.
4. `allure serve allure-results` shows steps, API request/response attachments, screenshots/traces on a deliberately failing test.
5. Push branch → GitHub Actions `smoke.yml` green; Allure report artifact downloadable.

## 7. Open points / later

- ~~Exact checkout success text & billing-address prefill~~ — resolved in step 8: success text is "Payment was successful" (`payment-success-message`); billing is prefilled from the profile, and proceed needs all six address fields, so `test_user` is registered with a full address.
- Regression scope later: register, contact form, filters/sort/pagination, favorites, invoices, admin, multi-browser matrix, Allure history on GitHub Pages.
