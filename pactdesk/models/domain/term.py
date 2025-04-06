from typing import Literal, TypeVar

from pydantic import BaseModel, field_validator


T = TypeVar("T", bound=BaseModel)


class Term(BaseModel):
    duration_amount: int
    duration_unit: Literal["years", "months"]

    @field_validator("duration_amount")  # type: ignore[misc]
    @classmethod
    def validate_duration_amount(cls: type[T], value: int) -> int:
        if value <= 0:
            err_msg = "Duration amount must be greater than zero"
            raise ValueError(err_msg)

        return value
