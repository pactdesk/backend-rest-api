from typing import Union

from pydantic import BaseModel


class ContextValue(BaseModel):
    value: str | int | None


class PartyContextValue(BaseModel):
    data: dict[str, str | int | None]


class PartyContext(BaseModel):
    data: dict[str, PartyContextValue]


class NormalContext(BaseModel):
    data: dict[str, str | int | None]


# Type aliases for convenience
ContextValueType = Union[str, int, None]
PartyContextType = dict[str, dict[str, ContextValueType]]
ContextType = dict[str, ContextValueType]
