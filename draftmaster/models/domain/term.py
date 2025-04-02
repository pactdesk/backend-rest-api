from typing import Literal

from pydantic import BaseModel, field_validator


class Term(BaseModel):
    duration_amount: int
    duration_unit: Literal["years", "months"]

    @field_validator("duration_amount")
    @classmethod
    def validate_duration_amount(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Duration amount must be greater than zero")

        return value
