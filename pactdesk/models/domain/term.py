"""
Term domain models for the PactDesk system.

This module defines the models for time-limited terms in contracts, which specify
the duration of contractual obligations. It provides validation to ensure that
duration amounts are positive values and that duration units are valid.
"""

from typing import Literal, TypeVar

from pydantic import BaseModel, field_validator


T = TypeVar("T", bound=BaseModel)


class Term(BaseModel):
    """
    Model for time-limited terms in contracts.

    This class represents a term that specifies the duration of a contractual
    obligation, such as the confidentiality period in a nondisclosure agreement.
    It includes both a duration amount and a unit of measurement.

    Attributes
    ----------
        duration_amount: The numerical value of the duration.
        duration_unit: The unit of measurement for the duration, either "years" or "months".
    """

    duration_amount: int
    duration_unit: Literal["years", "months"]

    @field_validator("duration_amount")  # type: ignore[misc]
    @classmethod
    def validate_duration_amount(cls: type[T], value: int) -> int:
        """
        Validate that the duration amount is greater than zero.

        This validator ensures that the duration amount is a positive value,
        which is a fundamental requirement for any valid term.

        Parameters
        ----------
            cls: The class object, automatically provided by the decorator.
            value: The duration amount to validate.

        Returns
        -------
            The validated duration amount.

        Raises
        ------
            ValueError: If the duration amount is less than or equal to zero.
        """
        if value <= 0:
            err_msg = "Duration amount must be greater than zero"
            raise ValueError(err_msg)

        return value
