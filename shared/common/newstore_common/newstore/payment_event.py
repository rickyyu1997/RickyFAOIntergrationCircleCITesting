from newstore_common.utils import compare_ordinal


class PaymentEventTransaction:

    def __init__(self, transaction, instrument):
        if transaction["instrument_id"] != instrument["id"]:
            raise Exception(f"Wrong instrument id {instrument['id']}")
        self.transaction = transaction
        self.instrument = instrument

    def get_provider(self) -> str:
        return self.instrument["payment_provider"]

    def get_amount(self):
        return self.transaction["amount"]

    def is_cash(self):
        return compare_ordinal(self.get_provider(), "cash")

    def get_instrument_id(self) -> str:
        return self.instrument["id"]

    def get_currency(self):
        return self.transaction["currency"]

    def get_attributes(self):
        return self.transaction["extended_attributes"]

    def get_id(self):
        return self.transaction["id"]

class RefundEventTransaction(PaymentEventTransaction):

    def __init__(self, transaction, instrument):
        super().__init__(transaction, instrument)

    def get_return_id(self):
        return self.transaction["correlation_id"]


class PaymentEvent:

    def __init__(self, event):
        self.event = event

    def get_instruments(self):
        return self.event["instruments"]

    def get_instrument(self, instrument_id):
        return next((i for i in self.get_instruments() if i["id"] == instrument_id), None)

    def get_order_id(self):
        return self.event["order_id"]

    def create_transaction(self, transaction) -> PaymentEventTransaction:
        instrument_id = transaction["instrument_id"]
        instrument = self.get_instrument(instrument_id)
        if not instrument:
            raise Exception(f"instrument does not exist {instrument_id}")
        return PaymentEventTransaction(transaction, instrument)

    def get_transactions(self) -> [PaymentEventTransaction]:
        for transaction in self.event["transactions"]:
            yield self.create_transaction(transaction)


class RefundEvent(PaymentEvent):

    def __init__(self, event):
        super().__init__(event)

    def get_transactions(self) -> [RefundEventTransaction]:
        return super().get_transactions()

    def create_transaction(self, transaction) -> RefundEventTransaction:
        instrument_id = transaction["instrument_id"]
        instrument = self.get_instrument(instrument_id)
        if not instrument:
            raise Exception(f"instrument does not exist {instrument_id}")
        return RefundEventTransaction(transaction, instrument)
