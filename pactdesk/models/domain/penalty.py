"""
Penalty domain models for the PactDesk system.

This module defines the models for penalty clauses in contracts, which specify
the consequences of breaching contractual obligations. It provides validation
to ensure that penalty amounts are positive values.
"""

from typing import TypeVar

from pydantic import BaseModel, field_validator


T = TypeVar("T", bound=BaseModel)


class Penalty(BaseModel):
    """
    Model for penalty clauses in contracts.

    This class represents a penalty clause that specifies the financial consequences
    of breaching a contract. It includes both an initial penalty amount for the
    first breach and a subsequent amount for any additional breaches.

    Attributes
    ----------
        initial_amount: The amount of the penalty for the first breach of contract.
        subsequent_amount: The amount of the penalty for any subsequent breaches.
    """

    initial_amount: int
    subsequent_amount: int

    @field_validator("initial_amount")  # type: ignore[misc]
    @classmethod
    def validate_initial_amount(cls: type[T], value: int) -> int:
        """
        Validate that the initial penalty amount is greater than zero.

        This validator ensures that the initial penalty amount is a positive value,
        which is a fundamental requirement for any valid penalty clause.

        Parameters
        ----------
            cls: The class object, automatically provided by the decorator.
            value: The initial penalty amount to validate.

        Returns
        -------
            The validated initial penalty amount.

        Raises
        ------
            ValueError: If the initial penalty amount is less than or equal to zero.
        """
        if value <= 0:
            err_msg = "Initial penalty amount must be greater than zero"
            raise ValueError(err_msg)

        return value

    @field_validator("subsequent_amount")  # type: ignore[misc]
    @classmethod
    def validate_subsequent_amount(cls: type[T], value: int) -> int:
        """
        Validate that the subsequent penalty amount is greater than zero.

        This validator ensures that the subsequent penalty amount is a positive value,
        which is a fundamental requirement for any valid penalty clause.

        Parameters
        ----------
            cls: The class object, automatically provided by the decorator.
            value: The subsequent penalty amount to validate.

        Returns
        -------
            The validated subsequent penalty amount.

        Raises
        ------
            ValueError: If the subsequent penalty amount is less than or equal to zero.
        """
        if value <= 0:
            err_msg = "Subsequent penalty amount must be greater than zero"
            raise ValueError(err_msg)

        return value
