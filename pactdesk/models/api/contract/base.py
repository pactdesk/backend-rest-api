"""Module for handling base contract request models.

This module defines the foundational models for contract requests in the API,
including validation logic and common attributes shared across different
contract types.
"""

from typing import TypeVar

from pydantic import BaseModel, field_validator

from pactdesk.models.domain.enum import ContractType, InformationRole, ManagementRole
from pactdesk.models.domain.party import LegalEntity, NaturalPerson, Party
from pactdesk.models.domain.role import Role


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

    contract_type: ContractType
    parties: dict[str, Party]
    applicable_law: str
    place_of_jurisdiction: str

    @field_validator("parties", mode="before")  # type: ignore[misc]
    @classmethod
    def convert_parties(cls, value: dict[str, dict], info) -> dict[str, Party]:  # type: ignore[no-untyped-def]
        """Convert raw party dictionaries to Party objects.

        This validator converts the raw party data from the request into proper
        Party objects (either NaturalPerson or LegalEntity) based on the party_type.

        Args:
            cls: The class object, automatically provided by the decorator.
            value (dict[str, dict]): Dictionary mapping party identifiers to raw
                party data dictionaries.

        Returns
        -------
            dict[str, Party]: Dictionary mapping party identifiers to Party objects.

        Raises
        ------
            ValueError: If an invalid party type is encountered.
        """
        converted_parties: dict[str, Party] = {}

        # Get the contract type from the validation context
        contract_type = info.data.get("contract_type")
        if not contract_type:
            err_msg = "Contract type must be specified before parties can be converted"
            raise ValueError(err_msg)

        # Get the appropriate role type for this contract
        role_type = cls.get_contract_role(ContractType(contract_type))

        for key, party_data in value.items():
            party_type = party_data.get("party_type")

            # Create a copy of the party data to avoid modifying the original
            party_data = party_data.copy()

            # Convert the role string to the appropriate enum
            if "role" in party_data:
                try:
                    party_data["role"] = role_type(party_data["role"])
                except ValueError as e:
                    err_msg = (
                        f"Invalid role value for {contract_type} contract: " f"{party_data['role']}"
                    )
                    raise ValueError(err_msg) from e

            if party_type == "natural_person":
                converted_parties[key] = NaturalPerson(**party_data)
            elif party_type == "legal_entity":
                converted_parties[key] = LegalEntity(**party_data)
            else:
                err_msg = f"Invalid party type: {party_type}"
                raise ValueError(err_msg)

        return converted_parties

    @field_validator("parties")  # type: ignore[misc]
    @classmethod
    def validate_parties(cls, value: dict[str, Party]) -> dict[str, Party]:
        """Validate that the parties dictionary contains at least one party.

        This validator ensures that every contract request has at least one party
        involved, which is a fundamental requirement for any valid contract.
        Without parties, a contract would have no subjects to bind, making it
        legally meaningless.

        Args:
            cls: The class object, automatically provided by the decorator.
            value (dict[str, Party]): Dictionary mapping party identifiers to Party
                objects, representing all entities involved in the contract.

        Returns
        -------
            dict[str, Party]: The validated parties dictionary,
                containing at least one party.

        Raises
        ------
            ValueError: If the parties dictionary is empty.
        """
        if not value:
            err_msg = "At least one party must be provided"
            raise ValueError(err_msg)

        return value

    @classmethod
    def get_contract_role(cls, contract_type: ContractType) -> type[Role]:
        """Get the appropriate role type for a given contract type.

        This method maps contract types to their corresponding role types,
        ensuring that the correct role model is used for validation and
        processing of contract requests.

        Args:
            contract_type (ContractType): The type of contract to get the role type for.

        Returns
        -------
            type[Role]: The role type class corresponding to the contract type.

        Raises
        ------
            ValueError: If no role type is defined for the given contract type.
        """
        role_types: dict[ContractType, type[Role]] = {
            ContractType.NONDISCLOSURE: InformationRole,
            ContractType.MANAGEMENT: ManagementRole,
        }

        if role_type := role_types.get(contract_type):
            return role_type

        err_msg = f"No role type defined for contract type: {contract_type}"
        raise ValueError(err_msg)
