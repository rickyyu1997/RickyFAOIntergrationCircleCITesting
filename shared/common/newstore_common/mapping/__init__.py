import logging

logger = logging.getLogger(__name__)
logging.basicConfig()


def has_key(fields, key):
    if isinstance(fields, list):
        return int(key) < len(fields)
    return key in fields


def get_key(fields, key):
    if isinstance(fields, list):
        return int(key)
    return str(key)


def find_value(original_key: str, current_fields: dict, current_key: str):
    keys = current_key.split("__")
    extracted_key = keys[0]

    if not has_key(current_fields, extracted_key):
        raise Exception(f"key not found at level: {current_key}. full key: {original_key}, fields: {current_fields}")

    value = current_fields[get_key(current_fields, extracted_key)]

    if len(keys) == 1:
        return value

    new_key = "__".join(keys[1:])
    return find_value(original_key, value, new_key)


def is_primitive(value) -> bool:
    primitive = (int, str, bool, float)
    return type(value) in primitive


def map_dict(mapping: dict, values: dict):
    mapped_fields = {}

    for mapped_key, ns_key in mapping.items():

        value = find_value(ns_key, values, ns_key)

        logger.info(f"extracted value {value} fom key {ns_key}")
        if not is_primitive(value):
            raise Exception(f"value is not primitive got type {type(value)}")

        mapped_fields[mapped_key] = value

    return mapped_fields
