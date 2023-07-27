from newstore_common.storage.payload_file import PayloadFile
from newstore_common.storage.response import Response


class CloudStorage:

    def upload(self, key: str, payload_file: PayloadFile) -> Response:
        raise Exception(f'upload function of a {self.__class__.__name__} class has not been implemented')

    def download(self, key: str) -> Response:
        raise Exception(f'download function of a {self.__class__.__name__} class has not been implemented')
