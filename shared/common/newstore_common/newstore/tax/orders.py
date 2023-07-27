import logging
from dataclasses import dataclass

from newstore_common.newstore.integration.orders import Order
from newstore_common.newstore.tax import Taxation

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ItemPrices:
    catalog: float
    gross: float
    net: float


class TaxHandler:

    def __init__(self, order: Order):
        self.order = order

    def get_taxation(self) -> Taxation:
        return self.order.get_taxation()

    def has_net_prices(self) -> bool:
        # taxation gross means prices are net and tax will be added later.
        return self.get_taxation() == Taxation.gross

    def get_net_catalog_price(self, prices: ItemPrices):
        net_price = prices.net
        gross_price = prices.gross
        catalog_price = prices.catalog
        if self.has_net_prices():
            return catalog_price
        tax_rate = 100  # discount is 100%
        if net_price > 0:  # if the price is larger than 0 the discount is not 100%
            tax_rate = round((gross_price / net_price) * 100)  # e.g. 120 für 20% sales tax

        # catalog is net or gross
        net_unit_price = round((catalog_price / tax_rate) * 100, 2)
        logger.info(f"Catalog price is gross. Calculated tax {tax_rate} net price: {net_unit_price}")
        return net_unit_price

    def get_item_net_prices(self, prices: ItemPrices):
        net_price = prices.net
        net_unit_price = self.get_net_catalog_price(prices)
        net_discount_amount = round(net_unit_price - net_price, 2)
        return net_unit_price, net_discount_amount
