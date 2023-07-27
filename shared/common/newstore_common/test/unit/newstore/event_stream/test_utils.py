from newstore_common.aws.context import FakeAwsContext
from newstore_common.newstore.event_stream import FulfillmentRequestItemsCompleted

from newstore_common.newstore.event_stream.utils import with_any

class TestUtils:

    def test_with_any(self):

        def method(event, context, raw_event):
            return event, context, raw_event

        raw_event = {
            "Records": [
                {
                    "body": "{\"tenant\": \"ganni\", \"name\": \"fulfillment_request.items_completed\", \"published_at\": \"2019-04-11T13: 19: 01.255Z\", \"payload\": {\"service_level\": \"LEVEL\", \"id\": \"1f3bc00b-4c07-4a52-a33b-6e622b57d1da\", \"order_id\": \"ac1e1b20-a22d-4772-8688-6c4195cd71ca\", \"logical_timestamp\": 175, \"fulfillment_location_id\": \"STRG\", \"associate_id\": \"unknown\", \"items\": [{\"id\": \"9ea84bce-a657-4962-885f-1b18059ce690\", \"product_id\": \"F317218008\"}]}}"
                }
            ]
        }

        ret = with_any(method)(raw_event, FakeAwsContext)
        assert type(ret[0]) == FulfillmentRequestItemsCompleted
        assert type(ret[1]) == type(FakeAwsContext)
        assert ret[2] == raw_event

    def test_with_any_extra_arg(self):

        def method(event,  context, raw_event, *arg4):
            return event, context, raw_event, arg4
        raw_event = {
            "Records": [
                {
                    "body": "{\"tenant\": \"ganni\", \"name\": \"fulfillment_request.items_completed\", \"published_at\": \"2019-04-11T13: 19: 01.255Z\", \"payload\": {\"service_level\": \"LEVEL\", \"id\": \"1f3bc00b-4c07-4a52-a33b-6e622b57d1da\", \"order_id\": \"ac1e1b20-a22d-4772-8688-6c4195cd71ca\", \"logical_timestamp\": 175, \"fulfillment_location_id\": \"STRG\", \"associate_id\": \"unknown\", \"items\": [{\"id\": \"9ea84bce-a657-4962-885f-1b18059ce690\", \"product_id\": \"F317218008\"}]}}"
                }
            ]
        }

        ret = with_any(method)(raw_event, FakeAwsContext, "test", "test2", "test3")
        assert type(ret[0]) == FulfillmentRequestItemsCompleted
        assert type(ret[1]) == type(FakeAwsContext)
        assert ret[2] == raw_event
        assert ret[3] == ("test", "test2", "test3")

    def test_with_any_extra_arg_receiving(self):

        def method(event,  context, raw_event, other_parameter, other_parameter2):
            return event, context, raw_event, other_parameter, other_parameter2
        raw_event = {
            "Records": [
                {
                    "body": "{\"tenant\": \"ganni\", \"name\": \"fulfillment_request.items_completed\", \"published_at\": \"2019-04-11T13: 19: 01.255Z\", \"payload\": {\"service_level\": \"LEVEL\", \"id\": \"1f3bc00b-4c07-4a52-a33b-6e622b57d1da\", \"order_id\": \"ac1e1b20-a22d-4772-8688-6c4195cd71ca\", \"logical_timestamp\": 175, \"fulfillment_location_id\": \"STRG\", \"associate_id\": \"unknown\", \"items\": [{\"id\": \"9ea84bce-a657-4962-885f-1b18059ce690\", \"product_id\": \"F317218008\"}]}}"
                }
            ]
        }

        ret = with_any(method)(raw_event, FakeAwsContext, "extra1", "extra2")
        assert type(ret[0]) == FulfillmentRequestItemsCompleted
        assert type(ret[1]) == type(FakeAwsContext)
        assert ret[2] == raw_event
        assert ret[3] == "extra1"
        assert ret[4] == "extra2"
