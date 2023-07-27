from newstore_common.json.decimal_encoder import DecimalToStringEncoder
from collections.abc import Iterator

from newstore_common.caching.cached_property import CachedProperty as OnlyUseThisCachedProperty


def compare_ordinal(value_1: str, value_2: str) -> bool:
    return value_1.lower().strip() == value_2.lower().strip()


def flatten(it: list):
    for x in it:
        # allow iterator for yields
        if isinstance(x, Iterator) or isinstance(x, list):
            yield from flatten(x)
        else:
            yield x


# Deprecated
# from newstore_common.caching.cached_property import CachedProperty
class CachedProperty(OnlyUseThisCachedProperty):
    pass


# Deprecated
# from newstore_common.json.decimal_encoder import DecimalToStringEncoder
class DecimalEncoder(DecimalToStringEncoder):
    pass