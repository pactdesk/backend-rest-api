"""Module for handling party-related models in contract documents.

This module defines the data models for different types of parties that can be involved
in a contract, including natural persons and legal entities. It includes validation
logic for addresses and party-specific attributes.
"""

import re
from typing import Annotated, Literal, Self, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

from pactdesk.models.domain.enum import CompanyType, InformationRole, PartyType


T = TypeVar("T", bound=BaseModel)


class BaseParty(BaseModel):
    """Base class for all party types in a contract.

    This class serves as the foundation for both natural persons and legal entities,
    providing the common structure for party identification.

    Attributes
    ----------
        party_type (str): The type of party (natural_person or legal_entity).
    """

    party_type: str


class Address(BaseModel):
    """Represents a physical address in a contract document.

    This class handles address formatting and validation, including postcode validation
    for Dutch addresses.

    Attributes
    ----------
        street_name (str): The name of the street.
        house_nr (str): The house number.
        city (str): The city name.
        postcode (str): The postal code (validated for Dutch format).
        suffix (str | None): Optional address suffix (e.g., apartment number).
        _formatted (str | None): The formatted address string.
    """

    street_name: str
    house_nr: str
    city: str
    postcode: str
    suffix: str | None = None
    _formatted: str | None = None

    @field_validator("postcode")  # type: ignore[misc]
    @classmethod
    def validate_postcode(cls: type[T], value: str) -> str:
        """Validate that the postcode matches the Dutch format.

        Args:
            value (str): The postcode to validate.

        Returns
        -------
            str: The validated postcode.

        Raises
        ------
            ValueError: If the postcode does not match the required format.
        """
        pattern = r"^[0-9]{4}([ ]?)[A-Z]{2}$"
        if not re.match(pattern, value):
            err_msg = (
                "Postcode must be 4 digits followed by 2 capital letters "
                "(with or without a space)"
            )
            raise ValueError(err_msg)

        return value

    @model_validator(mode="after")  # type: ignore[misc]
    def format_address(self) -> Self:
        """Format the address components into a single string.

        Returns
        -------
            Self: The instance with the formatted address.
        """
        self._formatted = f"{self.street_name} {self.house_nr}"
        if self.suffix:
            self._formatted += f" {self.suffix}"
        self._formatted += f", {self.postcode} {self.city}"
        return self


class NaturalPerson(BaseParty):
    """Represents a natural person as a party in a contract.

    This class extends BaseParty to include personal information specific to
    individuals, such as full name, address, and birth details.

    Attributes
    ----------
        party_type (Literal["natural_person"]): Always set to natural_person.
        full_name (str): The complete name of the person.
        address (Address): The person's physical address.
        date_of_birth (str): The person's date of birth.
        place_of_birth (str): The person's place of birth.
        country_of_birth (str): The person's country of birth.
        information_role (InformationRole | None): The person's role in the contract.
    """

    party_type: Literal["natural_person"] = PartyType.NATURAL_PERSON.value
    full_name: str
    address: Address
    date_of_birth: str
    place_of_birth: str
    country_of_birth: str
    information_role: InformationRole | None = None


class LegalEntity(BaseParty):
    """Represents a legal entity as a party in a contract.

    This class extends BaseParty to include business-specific information such as
    company type, registration details, and authorized signatory.

    Attributes
    ----------
        party_type (Literal["legal_entity"]): Always set to legal_entity.
        company_type (CompanyType): The type of legal entity.
        name (str): The legal name of the entity.
        registered_address (Address): The entity's registered address.
        country_of_incorporation (str): The country where the entity is incorporated.
        kvk_nr (str): The Chamber of Commerce registration number.
        signatory_name (str): The name of the authorized signatory.
        information_role (InformationRole | None): The entity's role in the contract.
    """

    party_type: Literal["legal_entity"] = PartyType.LEGAL_ENTITY.value
    company_type: CompanyType
    name: str
    registered_address: Address
    country_of_incorporation: str
    kvk_nr: str
    signatory_name: str
    information_role: InformationRole | None = None


Party = Annotated[NaturalPerson | LegalEntity, Field(discriminator="party_type")]
