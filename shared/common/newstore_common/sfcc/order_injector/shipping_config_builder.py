from dataclasses import dataclass
from newstore_common.sfcc.xml_api.order.order_data import Shipment


@dataclass(frozen=True)
class ShippingConfig:
    service_level: str
    shipping_carrier_name: str
    shipping_type: str
    fulfillment_node_id: str


class ShippingConfigBuilder:
    def get_shipping_config(self, shipment: Shipment) -> ShippingConfig:
        raise NotImplementedError(f"[{self.__class__.__name__}] get_shipping_config() must be implemented")
