"""
Base contract request models for the PactDesk API.

This module defines the foundational contract request models that serve as the base
for all specific contract types in the PactDesk system. It provides the common
structure and validation logic that all contract requests must adhere to, ensuring
consistency across different contract types while allowing for specialized behavior
in derived classes.
"""

from typing import TypeVar

from pydantic import BaseModel, field_validator

from pactdesk.models.domain.party import LegalEntity, NaturalPerson, Party


T = TypeVar("T", bound=BaseModel)


class BaseContractRequest(BaseModel):
    """
    Base model for all contract requests in the PactDesk system.

    This class defines the common structure and validation rules that all contract
    requests must follow. It establishes the fundamental contract properties such
    as contract type, parties involved, applicable law, and jurisdiction. The class
    implements validation logic to ensure that contract requests contain at least
    one party, maintaining the integrity of the contract generation process.

    This base class is designed to be extended by specific contract type models
    that add additional fields and validation rules relevant to their particular
    contract category.

    Attributes
    ----------
        contract_type: The type of contract being requested, which determines the
            specific template and validation rules to be applied.
        parties: A dictionary mapping party identifiers to Party objects, representing
            all entities involved in the contract. Each party can be either a natural
            person or a legal entity.
        applicable_law: The legal jurisdiction whose laws will govern the interpretation
            and enforcement of the contract.
        place_of_jurisdiction: The specific location where any legal proceedings
            related to the contract must be conducted.
    """

    contract_type: str
    parties: dict[str, Party]
    applicable_law: str
    place_of_jurisdiction: str

    @field_validator("parties")  # type: ignore[misc]
    @classmethod
    def validate_parties(
        cls: type[T], value: dict[str, Party]
    ) -> dict[str, NaturalPerson | LegalEntity]:
        """
        Validates that the parties dictionary contains at least one party.

        This validator ensures that every contract request has at least one party
        involved, which is a fundamental requirement for any valid contract.
        Without parties, a contract would have no subjects to bind, making it
        legally meaningless.

        Parameters
        ----------
            cls: The class object, automatically provided by the decorator.
            value: A dictionary mapping party identifiers to Party objects,
                representing all entities involved in the contract.

        Returns
        -------
            The validated parties dictionary, containing at least one party.

        Raises
        ------
            ValueError: If the parties dictionary is empty.
        """
        if not value:
            err_msg = "At least one party must be provided"
            raise ValueError(err_msg)

        return value
