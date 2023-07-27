from newstore_common.newstore.tax import Taxation


class Order:

    def __init__(self, ns_order: {}):
        self.ns_order = ns_order

    def get_taxation(self) -> Taxation:
        tax = self.ns_order["taxation"]
        return Taxation.net if tax == "net" else Taxation.gross
