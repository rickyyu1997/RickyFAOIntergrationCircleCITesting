from dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    @property
    def error(self) -> str:
        raise NotImplementedError(f"[{self.__class__.__name__}] error() must be implemented")