import dataclasses
import decimal
import logging
from enum import Enum
from typing import TypeVar, Generic, Dict

import boto3
from dacite import from_dict, Config

from newstore_common.utils import CachedProperty

logger = logging.getLogger(__name__)
logging.basicConfig()

T = TypeVar('T')


@dataclasses.dataclass(frozen=True)
class KeyDefinition:
    name: str
    value: str


class BaseStore(Generic[T]):

    def __init__(self, table_name: str, resource=None):
        self.table_name = table_name
        self.resource = resource

    @CachedProperty
    def _table(self):
        if self.resource is None:
            self.resource = boto3.resource('dynamodb')
        return self.resource.Table(self.table_name)

    def put(self, entry: T):
        logger.info(f"inserting item into DB: {entry}")
        response = self._table.put_item(
            Item=self._marshal(dataclasses.asdict(entry))
        )
        logger.info(f"got dynamo response {response}")
        return response

    def get(self, data_class: dataclasses.dataclass, keys: [KeyDefinition]):
        db_keys = {key.name: key.value for key in keys}
        result = self._table.get_item(Key=db_keys)
        return self._to_dataclass(dataclass=data_class, item=result['Item'])

    def query(self, dataclass, index=None, condition=None, values=None) -> [T]:
        args = {
            "KeyConditionExpression": condition,
            "ExpressionAttributeValues": values
        }
        if index:
            args["IndexName"] = index
        response = self._table.query(**args)
        # raise Exception(response)
        logger.info(f"got query response {response}")
        items = response["Items"]
        if len(items) < 1:
            return []

        for item in items:
            yield from_dict(data_class=dataclass, data=item, config=self._get_config())

    def _get_config(self) -> Config:
        return Config(cast=[Enum])

    def _to_dataclass(self, item: Dict, dataclass):
        return from_dict(data_class=dataclass, data=item, config=self._get_config())

    def _marshal(self, entry: Dict) -> Dict:
        ret = {}
        for k, v in entry.items():
            if isinstance(v, dict):
                ret[k] = self._marshal(v)
            elif isinstance(v, list):
                ret[k] = [self._marshal(i) if isinstance(
                    i, dict) else i for i in v]
            elif isinstance(v, float):
                ret[k] = decimal.Decimal(str(v))
            elif isinstance(v, Enum):
                ret[k] = v.value
            elif v == '':
                ret[k] = None
            else:
                ret[k] = v
        return ret
