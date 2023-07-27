import logging
import json

import requests
from newstore_common.auth.requests import BearerAuth

logger = logging.getLogger(__name__)
logging.basicConfig()


class Sender:
    def __init__(self, mail: str, name: str):
        self.mail = mail
        self.name = name


class SalesForceError(Exception):
    """Exception for SFMC errors"""
    pass


class MessagingApi:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self) -> BearerAuth:
        auth_url = "https://auth.exacttargetapis.com/v1/requestToken"

        response = requests.post(auth_url, data={
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        })
        response.raise_for_status()
        return BearerAuth(response.json()["accessToken"])

    def send(self, definition_id: str, sender: Sender, recipient_email: str, subscriber_attributes: dict, endpoint: str = 'OrderStatus'):
        send_url = f"https://www.exacttargetapis.com/messaging/v1/messageDefinitionSends/key:{endpoint}/send"

        attributes = {**subscriber_attributes, **{
            "EmailAddress": recipient_email,
            "SubscriberKey": recipient_email,
            "EmailType": definition_id
        }}

        request = {
            "To": {
                "Address": recipient_email,
                "SubscriberKey": recipient_email,
                "ContactAttributes": {
                    "SubscriberAttributes": attributes
                }
            },
            "Options": {
                "RequestType": "SYNC"
            }
        }

        if sender is not None:
            request["From"] = {
                "Address": sender.mail,
                "Name": sender.name
            }

        logger.info(f"Sending api request: {json.dumps(request, indent=4)} with id {definition_id}")

        response = requests.post(send_url, json=request, auth=self.get_token())

        logger.info(f"Got response {json.dumps(response.json(), indent=4)}")

        response.raise_for_status()
        has_errors = any(x['hasErrors'] for x in response.json()['responses'])
        if has_errors:
            error_txt = ''
            for error in response.json()['responses']:
                if error['hasErrors']:
                    #some times it has messages, sometimes messageErrors. IDK why
                    error_msgs = error.get('messageErrors', [])
                    error_txt += '\n'.join([f"Error {x['messageErrorCode']}: {x['messageErrorStatus']}" for x in error_msgs])
                    error_txt += '\n'.join([x for x in error.get(['messages'], [])])
            raise SalesForceError(f"SFMC error: {error_txt}")
