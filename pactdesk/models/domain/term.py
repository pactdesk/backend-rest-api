"""Module for handling term definitions in contract documents.

This module defines the data model for contract terms, which specify the duration
and unit of time for contractual obligations. It includes validation to ensure
term durations are positive values.
"""

from typing import Literal, TypeVar

from pydantic import BaseModel, field_validator


T = TypeVar("T", bound=BaseModel)


class Term(BaseModel):
    """Represents a time period in a contract.

    This class defines the structure for specifying contract durations, including
    both the amount and unit of time.

    Attributes
    ----------
        duration_amount (int): The number of time units.
        duration_unit (Literal["years", "months"]): The unit of time (years or months).
    """

    duration_amount: int
    duration_unit: Literal["years", "months"]

    @field_validator("duration_amount")  # type: ignore[misc]
    @classmethod
    def validate_duration_amount(cls: type[T], value: int) -> int:
        """Validate that the duration amount is positive.

        Args:
            value (int): The duration amount to validate.

        Returns
        -------
            int: The validated duration amount.

        Raises
        ------
            ValueError: If the duration amount is zero or negative.
        """
        if value <= 0:
            err_msg = "Duration amount must be greater than zero"
            raise ValueError(err_msg)

        return value
