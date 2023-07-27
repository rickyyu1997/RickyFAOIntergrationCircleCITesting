# Description

General utility library.

# Functions

## Cash rounding

If paid in cash, some amounts will be rounded. This depends on the currency since some countries decided to discontinue coins with small worth.

The CashRounding class returns the rounded amount based on the currency paid. Note: currently only DKK is supported. More currencies can be configued in cash_mapping.json

Example:

```python
from newstore_common.payments.cash import CashRounding


transaction = {
    "amount" : 1200.76,
    "currency" : "DKK"
}

rounding_handler = CashRounding()
rounded = rounding_handler.round_amount(transaction["currency"], transaction["amount"]) # shpuld be 1201.00 for DKK

```


## Payment events

Wraps the newstore event stream payment payloads to an easy to use format.

Example:

````python
from newstore_common.newstore.payment_event import PaymentEvent, RefundEvent

ns_event = {} # from event stream

event = PaymentEvent(ns_event["payload"])

transactions = event.get_transactions()
for transaction in transactions:
    print(transaction.get_provider())

````


## AWS - DynamoStore
AWS repository like DynamoDB wrapper. Extend class for easier usage.

```python

from newstore_common.aws.dynamo_db import DynamoStore

class ReportsStore(DynamoStore):

    def __init__(self):
        super().__init__("table_name")


    def upsert(self, id, entry):
        entry.update({
            "id" : id
        })     
        return self.put_item(entry)

```

## Utils
"newstore_common.utils" namespace contains simple, reusable functions.