"""Module for handling base contract request models.

This module defines the foundational models for contract requests in the API,
including validation logic and common attributes shared across different
contract types.
"""

from typing import TypeVar

from pydantic import BaseModel, field_validator

from pactdesk.models.domain.party import LegalEntity, NaturalPerson, Party


T = TypeVar("T", bound=BaseModel)


class BaseContractRequest(BaseModel):
    """Base model for contract generation requests.

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
        contract_type (str): The type of contract being requested, which determines
            the specific template and validation rules to be applied.
        parties (dict[str, Party]): Dictionary mapping party identifiers to Party
            objects, representing all entities involved in the contract. Each party
            can be either a natural person or a legal entity.
        applicable_law (str): The legal jurisdiction whose laws will govern the
            interpretation and enforcement of the contract.
        place_of_jurisdiction (str): The specific location where any legal
            proceedings related to the contract must be conducted.
    """

    contract_type: str
    parties: dict[str, Party]
    applicable_law: str
    place_of_jurisdiction: str

    @classmethod
    @field_validator("parties")  # type: ignore[misc]
    def validate_parties(
        cls: type[T], value: dict[str, Party]
    ) -> dict[str, NaturalPerson | LegalEntity]:
        """Validate that the parties dictionary contains at least one party.

        This validator ensures that every contract request has at least one party
        involved, which is a fundamental requirement for any valid contract.
        Without parties, a contract would have no subjects to bind, making it
        legally meaningless.

        Args:
            cls (type[T]): The class object, automatically provided by the decorator.
            value (dict[str, Party]): Dictionary mapping party identifiers to Party
                objects, representing all entities involved in the contract.

        Returns
        -------
            dict[str, NaturalPerson | LegalEntity]: The validated parties dictionary,
                containing at least one party.

        Raises
        ------
            ValueError: If the parties dictionary is empty.
        """
        if not value:
            err_msg = "At least one party must be provided"
            raise ValueError(err_msg)

        return value
