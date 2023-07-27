import decimal
import logging

import boto3

logger = logging.getLogger(__name__)
logging.basicConfig()


class DynamoStore:

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.table = None

    def get_table(self):
        if self.table is None:
            dynamo_db = boto3.resource('dynamodb')
            self.table = dynamo_db.Table(self.table_name)
        return self.table

    def put_item(self, entry):
        response = self.get_table().put_item(
            Item=self.marshal(entry)
        )
        logger.info(f"Got response {response}")
        return response

    def get_item(self, key: {}):
        try:
            response = self.get_table().get_item(
                Key=key
            )
            logger.info(f"Got response {response}")
            return response["Item"]
        except KeyError:
            return None

    def delete_item(self, key: {}):
        try:
            response = self.get_table().delete_item(
                Key=key
            )
            logger.info(f"Got response {response}")
            return response
        except KeyError:
            return None

    def query(self, index, condition, values):
        response = self.get_table().query(
            IndexName=index,
            KeyConditionExpression=condition,
            ExpressionAttributeValues=values
        )
        logger.info(f"Got query response {response}")
        return response["Items"]

    def marshal(self, entry):
        ret = {}
        for k, v in entry.items():
            if isinstance(v, dict):
                ret[k] = self.marshal(v)
            elif isinstance(v, list):
                ret[k] = [self.marshal(i) if isinstance(
                    i, dict) else i for i in v]
            elif isinstance(v, float):
                ret[k] = decimal.Decimal(str(v))
            elif v == '':
                ret[k] = None
            else:
                ret[k] = v
        return ret
