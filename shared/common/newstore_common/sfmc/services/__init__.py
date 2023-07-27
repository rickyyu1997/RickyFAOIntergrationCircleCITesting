from newstore_common.enqueuing import HandlerBase
from newstore_common.sfmc.api import Sender, MessagingApi
from newstore_common.sfmc.services.mail_service import MailService
from newstore_common.sfmc.services.mapping import JsonMappingProvider


def create_service(handler: HandlerBase) -> MailService:
    mapping_provider = JsonMappingProvider(handler.context["config_path"], handler.context["tenant"])

    api = MessagingApi(handler.context["client_id"], handler.context["client_secret"])

    if "sender_mail" in handler.context and "sender_name" in handler.context:
        sender = Sender(handler.context["sender_mail"], handler.context["sender_name"])
    else:
        sender = None

    return MailService(handler.connector, mapping_provider, api, sender)
