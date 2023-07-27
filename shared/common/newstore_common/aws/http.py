import json


def api_status(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }
