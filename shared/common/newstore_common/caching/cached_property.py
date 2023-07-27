from datetime import timedelta, datetime


class CachedProperty(object):
    """ @CachedProperty
        @CachedProperty()
        @CachedProperty(max_age=3600)
    """
    def __init__(self, max_age=None):
        if callable(max_age):
            func = max_age
            max_age = None
        else:
            func = None
        self.max_age = max_age if max_age and max_age > 0 else None
        self._set_meta_data(func)

    def __call__(self, func):
        self._set_meta_data(func)
        return self

    def __get__(self, instance, clazz):
        if instance is None:
            return self

        instance_dict = instance.__dict__
        now = datetime.now()
        name = self.__name__
        if name in instance_dict:
            value, ttl = instance_dict[name]
            if not ttl:
                return value
            if now < ttl:
                return value

        value = self.func(instance)
        if self.max_age:
            instance_dict[name] = (value, now + timedelta(seconds=self.max_age))
        else:
            instance_dict[name] = (value, None)
        return value

    def __delete__(self, instance):
        instance.__dict__.pop(self.__name__, None)

    def _set_meta_data(self, func):
        self.func = func
        if func:
            self.__doc__ = func.__doc__
            self.__name__ = func.__name__
            self.__module__ = func.__module__
