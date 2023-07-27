import json
import os
import logging

from newstore_common.utils import CachedProperty

logger = logging.getLogger(__name__)
logging.basicConfig()


class MappingDefinition:

    def __init__(self, event_key: str, template_id: str, fields: dict):
        self.template_id = template_id
        self.fields = fields
        self.event_key = event_key


class MappingProvider:

    def get_definition(self, event_key: str) -> MappingDefinition:
        raise NotImplementedError

    def has_definition(self, event_key: str) -> bool:
        raise NotImplementedError


class JsonMappingProvider(MappingProvider):

    def __init__(self, config_path: str, tenant: str):
        self.tenant = tenant
        self.config_path = config_path

    @CachedProperty
    def config(self):
        path = os.path.join(self.config_path, f"mapping.{self.tenant}.json")
        logger.info(f"loading config from path {path}")
        with open(path) as handle:
            return json.loads(handle.read())

    def has_definition(self, event_key: str) -> bool:
        return event_key in self.config

    def get_defaults(self, event_key: str) -> dict:
        config = self.config[event_key]
        defaults = config.get("defaults", [])
        result = {}
        for item in defaults:
            result.update(self.get_definition(item).fields)
        return result

    def get_definition(self, event_key: str) -> MappingDefinition:
        if not self.has_definition(event_key):
            raise Exception(f"no config found for {event_key}")
        config = self.config[event_key]
        fields = self.get_defaults(event_key)
        fields.update(config["fields"])
        return MappingDefinition(event_key, config.get("template_id"), fields)
