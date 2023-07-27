from newstore_common.aws.http import api_status


class Response:

    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def is_successful(self):
        # Is true for 200 - 399
        return self.status_code // 200 == 1

    def as_dict(self):
        return api_status(self.status_code, self.body)