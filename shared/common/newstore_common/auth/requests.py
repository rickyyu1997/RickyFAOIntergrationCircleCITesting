from requests.auth import AuthBase


class BearerAuth(AuthBase):

    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token

    def __call__(self, r):
        r.headers['Authorization'] = f"Bearer {self.bearer_token}"
        return r
