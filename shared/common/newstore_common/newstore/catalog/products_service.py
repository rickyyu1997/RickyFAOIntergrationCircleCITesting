from enum import Enum

from newstore_adapter.connector import NewStoreConnector

PRODUCTS_CACHE = {}


class IdType(Enum):
    ean = 1
    sku = 2


class ProductsHelper:

    def __init__(self, connector: NewStoreConnector):
        self.connector = connector

    def get_product(self, product_id: str, id_type: IdType) -> {}:
        if not self._is_cached(product_id, id_type):
            result = self.connector.get_product(
                product_id, "storefront-catalog-en", "en-US", id_type=id_type.name)
            if result is None:
                raise Exception(f"Product with {id_type.name} not found: {product_id}")
            self._cache_product(product_id, result)
        return self._get_cached(product_id, id_type)

    def _cache_product(self, product_id: str, product) -> {}:
        PRODUCTS_CACHE[self._get_key(product_id, IdType.sku)] = product
        PRODUCTS_CACHE[self._get_key(product_id, IdType.ean)] = product

    def _get_cached(self, product_id: str, id_type: IdType):
        return PRODUCTS_CACHE[self._get_key(product_id, id_type)]

    def _get_key(self, product_id: str, id_type: IdType):
        return f"{id_type}_{product_id}"

    def _is_cached(self, product_id: str, id_type: IdType) -> bool:
        return self._get_key(product_id, id_type) in PRODUCTS_CACHE

    def get_ean(self, sku: str) -> str:
        return self.get_product(sku, IdType.sku)["external_identifiers"]["ean13"]

    def get_eans(self, skus: [str]) -> {str, str}:
        sku_ean_map = {}
        for sku in skus:
            sku_ean_map[sku] = self.get_ean(sku)
        return sku_ean_map

    def get_sku(self, ean: str):
        return self.get_product(ean, IdType.ean)["product_id"]
