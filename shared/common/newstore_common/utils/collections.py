from itertools import chain, islice


def chunk_iterable(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


class GeneratorResult:

    def __init__(self, count: int, generator):
        self.count = count
        self.generator = generator
