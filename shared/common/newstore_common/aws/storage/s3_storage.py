import logging
import boto3
import json

from newstore_common.storage.cloud_storage import CloudStorage
from newstore_common.storage.payload_file import PayloadFile
from newstore_common.storage.response import Response

logger = logging.getLogger(__name__)


class S3Storage(CloudStorage):

    def __init__(self, bucket: str = None):
        if bucket is None:
            raise Exception('Bucket was None')

        self.client = boto3.client('s3')
        self.bucket = bucket

    def upload(self, key=None, payload_file: PayloadFile = None) -> Response:
        if key is None or payload_file is None:
            raise Exception('Uploading to s3 bucket requires at least a key and file')

        response = self.client.put_object(
            Body=payload_file.content,
            ContentType=payload_file.content_type,
            ContentEncoding=payload_file.encoding,
            Bucket=self.bucket,
            Key=key
        )
        logger.info('S3 put_object response:' + json.dumps(response, indent=4))
        return Response(200, 'Success')

    def download(self, key=None) -> Response:
        if key is None:
            raise Exception('Downloading from s3 bucket requires key')

        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )

        bytestream = response['Body']
        body = bytestream.read()
        return Response(200, body)
