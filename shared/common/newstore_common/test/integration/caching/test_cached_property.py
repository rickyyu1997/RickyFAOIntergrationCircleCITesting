import uuid
from datetime import datetime
from time import sleep
from newstore_common.caching.cached_property import CachedProperty


class TestCachedProperty:

    @staticmethod
    def _get_uuid():
        return str(uuid.uuid4())

    @CachedProperty(max_age=1)
    def get_cached_property_one_second(self):
        return self._get_uuid()

    @CachedProperty(max_age=None)
    def get_cached_property_none(self):
        return self._get_uuid()

    @CachedProperty()
    def get_cached_property_infinite_callable(self):
        return self._get_uuid()

    @CachedProperty
    def get_cached_property_infinite(self):
        return self._get_uuid()

    def test_cached_property_one_second(self):
        expected = self.get_cached_property_one_second
        current1 = self.get_cached_property_one_second
        current2 = self.get_cached_property_one_second
        assert expected == current1 == current2, f"{expected} == {current1} == {current2}"
        assert "get_cached_property_one_second" in self.__dict__

        sleep(3)
        current3 = self.get_cached_property_one_second
        assert expected != current3, f"{expected} == {current3}"

        current4 = self.get_cached_property_one_second
        assert current3 == current4, f"{current3} == {current4}"

    def test_cached_property_one_second_internal(self):
        expected = self.get_cached_property_one_second
        assert "get_cached_property_one_second" in self.__dict__, "No cache entry"
        stored = self.__dict__["get_cached_property_one_second"]
        assert type(stored[0]) == str and stored[0] == expected, "Cached value not valid"
        assert type(stored[1]) == datetime, "Cached TTL not valid"

    def test_cached_property_none(self):
        expected = self.get_cached_property_none
        current1 = self.get_cached_property_none
        current2 = self.get_cached_property_none

        assert expected == current1 == current2, f"{expected} == {current1} == {current2}"

    def test_cached_property_none_internal(self):
        expected = self.get_cached_property_none
        assert "get_cached_property_none" in self.__dict__, "No cache entry"
        stored = self.__dict__["get_cached_property_none"]
        assert type(stored[0]) == str and stored[0] == expected, "Cached value not valid"
        assert stored[1] is None, "Cached TTL not valid"

    def test_cached_property_callable(self):
        expected = self.get_cached_property_infinite_callable
        current1 = self.get_cached_property_infinite_callable
        current2 = self.get_cached_property_infinite_callable

        assert expected == current1 == current2, f"{expected} == {current1} == {current2}"

    def test_cached_property_callable_internal(self):
        expected = self.get_cached_property_infinite_callable
        assert "get_cached_property_infinite_callable" in self.__dict__, "No cache entry"
        stored = self.__dict__["get_cached_property_infinite_callable"]
        assert type(stored[0]) == str and stored[0] == expected, "Cached value not valid"
        assert stored[1] is None, "Cached TTL not valid"

    def test_cached_property_infinite(self):
        expected = self.get_cached_property_infinite
        current1 = self.get_cached_property_infinite
        current2 = self.get_cached_property_infinite

        assert expected == current1 == current2, f"{expected} == {current1} == {current2}"

    def test_cached_property_infinite_internal(self):
        expected = self.get_cached_property_infinite
        assert "get_cached_property_infinite" in self.__dict__, "No cache entry"
        stored = self.__dict__["get_cached_property_infinite"]
        assert type(stored[0]) == str and stored[0] == expected, "Cached value not valid"
        assert stored[1] is None, "Cached TTL not valid"
