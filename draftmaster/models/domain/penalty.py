from pydantic import BaseModel, field_validator


class Penalty(BaseModel):
    initial_amount: int
    subsequent_amount: int

    @field_validator("initial_amount")
    @classmethod
    def validate_initial_amount(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Initial penalty amount must be greater than zero")

        return value

    @field_validator("subsequent_amount")
    @classmethod
    def validate_subsequent_amount(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Subsequent penalty amount must be greater than zero")

        return value
