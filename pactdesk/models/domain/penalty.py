"""Module for handling penalty clauses in contract documents.

This module defines the data model for penalty clauses, which specify the financial
consequences of breaching contract terms. It includes validation to ensure penalty
amounts are positive values.
"""

from typing import TypeVar

from pydantic import BaseModel, field_validator


T = TypeVar("T", bound=BaseModel)


class Penalty(BaseModel):
    """Represents a penalty clause in a contract.

    This class defines the structure for penalty amounts, including both initial
    and subsequent penalties for contract breaches.

    Attributes
    ----------
        initial_amount (int): The amount for the first breach.
        subsequent_amount (int): The amount for any subsequent breaches.
    """

    initial_amount: int
    subsequent_amount: int

    @field_validator("initial_amount")  # type: ignore[misc]
    @classmethod
    def validate_initial_amount(cls: type[T], value: int) -> int:
        """Validate that the initial penalty amount is positive.

        Args:
            value (int): The penalty amount to validate.

        Returns
        -------
            int: The validated penalty amount.

        Raises
        ------
            ValueError: If the penalty amount is zero or negative.
        """
        if value <= 0:
            err_msg = "Initial penalty amount must be greater than zero"
            raise ValueError(err_msg)

        return value

    @field_validator("subsequent_amount")  # type: ignore[misc]
    @classmethod
    def validate_subsequent_amount(cls: type[T], value: int) -> int:
        """Validate that the subsequent penalty amount is positive.

        Args:
            value (int): The penalty amount to validate.

        Returns
        -------
            int: The validated penalty amount.

        Raises
        ------
            ValueError: If the penalty amount is zero or negative.
        """
        if value <= 0:
            err_msg = "Subsequent penalty amount must be greater than zero"
            raise ValueError(err_msg)

        return value
