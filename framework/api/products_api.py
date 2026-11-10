import httpx


class ProductsApi:
    """Catalog endpoints: products, categories, brands."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list_products(self, page: int = 1) -> httpx.Response:
        return self._client.get("/products", params={"page": page})

    def get_product(self, product_id: str) -> httpx.Response:
        return self._client.get(f"/products/{product_id}")

    def categories_tree(self) -> httpx.Response:
        return self._client.get("/categories/tree")

    def brands(self) -> httpx.Response:
        return self._client.get("/brands")
