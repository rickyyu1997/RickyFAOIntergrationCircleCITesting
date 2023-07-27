import requests

from newstore_common.auth.requests import BearerAuth


class TokenHandler:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def is_associate(self, jwt_token: str) -> (bool, {}):
        url = f"{self.base_url}/v0/c/user_configuration"

        result = requests.get(url, auth=BearerAuth(jwt_token))
        if 400 <= result.status_code < 500:
            return False, None
        result.raise_for_status() # only throw server errors

        return True, result.json()
