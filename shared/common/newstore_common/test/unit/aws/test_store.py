from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from unittest.mock import MagicMock

import boto3
from botocore.stub import Stubber

from newstore_common.aws.dynamo.base_store import BaseStore


class EnumTest(Enum):
    KeyOne = "sd"


@dataclass(frozen=True)
class SampleFloat:
    float_test: float


@dataclass(frozen=True)
class SampleEnum:
    enum_test: EnumTest


class TypeT:
    pass


class GenericStore(BaseStore[TypeT]):
    pass


class TestStore:

    # def setup_class(self):
    #     raise Exception()

    def set_up(self):
        resource = boto3.resource('dynamodb')
        stubber = Stubber(resource.meta.client)
        store = BaseStore("name", resource=resource)
        return store, stubber

    # def test_t(self):
    #     store = GenericStore("test")
    #
    #     store.get(data_class=TypeT)

    def test_float(self):
        test_data = SampleFloat(float_test=1.0)
        expected_output = {'Item': {'float_test': Decimal('1.0')}, 'TableName': 'name'}
        store, stubber = self.set_up()
        stubber.add_response("put_item", service_response={}, expected_params=expected_output)
        stubber.activate()
        store.put(test_data)

        # assert Decimal(1.0) == output["test"]

    def test_enum(self):
        store, stubber = self.set_up()

        test_data = SampleEnum(enum_test=EnumTest.KeyOne)
        expected_output = {'Item': {'enum_test': test_data.enum_test.value}, 'TableName': 'name'}

        stubber.add_response("put_item", service_response={}, expected_params=expected_output)
        stubber.activate()
        store.put(test_data)

    def test_query_enum(self):
        expected_output = SampleEnum(enum_test=EnumTest.KeyOne)
        store = BaseStore("name")
        return_value = {
            "Items": [
                {
                    "enum_test": expected_output.enum_test.value
                }
            ]
        }
        table = MagicMock()
        table.query.return_value = return_value
        store._table = table
        response = list(store.query(SampleEnum))[0]
        assert response == expected_output
