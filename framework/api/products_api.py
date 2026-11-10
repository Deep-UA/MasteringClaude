import allure
import httpx


class ProductsApi:
    """Catalog endpoints: products, categories, brands."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_products(self, page: int = 1) -> httpx.Response:
        with allure.step(f"API: list products (page {page})"):
            return self._client.get("/products", params={"page": page})

    def get_product(self, product_id: str) -> httpx.Response:
        with allure.step(f"API: get product {product_id}"):
            return self._client.get(f"/products/{product_id}")

    def categories_tree(self) -> httpx.Response:
        with allure.step("API: get categories tree"):
            return self._client.get("/categories/tree")

    def brands(self) -> httpx.Response:
        with allure.step("API: get brands"):
            return self._client.get("/brands")
