from typing import TypeVar

from pydantic import BaseModel, field_validator


T = TypeVar("T", bound=BaseModel)


class Penalty(BaseModel):
    initial_amount: int
    subsequent_amount: int

    @field_validator("initial_amount")  # type: ignore[misc]
    @classmethod
    def validate_initial_amount(cls: type[T], value: int) -> int:
        if value <= 0:
            err_msg = "Initial penalty amount must be greater than zero"
            raise ValueError(err_msg)

        return value

    @field_validator("subsequent_amount")  # type: ignore[misc]
    @classmethod
    def validate_subsequent_amount(cls: type[T], value: int) -> int:
        if value <= 0:
            err_msg = "Subsequent penalty amount must be greater than zero"
            raise ValueError(err_msg)

        return value
