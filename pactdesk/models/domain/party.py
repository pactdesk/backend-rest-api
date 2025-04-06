"""
Party domain models for the PactDesk system.

This module defines the models for parties involved in contracts, including
natural persons and legal entities. It provides validation and formatting
capabilities for party information such as addresses and postcodes.
"""

import re
from typing import Annotated, Literal, Self, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

from pactdesk.models.domain.enum import CompanyType, InformationRole, PartyType


T = TypeVar("T", bound=BaseModel)


class BaseParty(BaseModel):
    """
    Base model for all party types in the PactDesk system.

    This class serves as the foundation for all party models, providing a common
    structure for party identification and role assignment.

    Attributes
    ----------
        party_type: The type of party, which determines the specific attributes
            and validation rules to be applied.
    """

    party_type: str


class Address(BaseModel):
    """
    Model for address information in the PactDesk system.

    This class represents a physical address with validation for postcodes and
    automatic formatting of the complete address string.

    Attributes
    ----------
        street_name: The name of the street.
        house_nr: The house or building number.
        city: The city or locality.
        postcode: The postal code, which must follow the Dutch format.
        suffix: Optional suffix for the house number (e.g., "A", "B").
        _formatted: The complete formatted address string, generated automatically.
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
        """
        Validate that the postcode follows the Dutch format.

        This validator ensures that the postcode consists of 4 digits followed by
        2 capital letters, with an optional space between them.

        Parameters
        ----------
            cls: The class object, automatically provided by the decorator.
            value: The postcode string to validate.

        Returns
        -------
            The validated postcode string.

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
        """
        Format the complete address string.

        This validator combines all address components into a single formatted
        string, which is stored in the _formatted attribute.

        Returns
        -------
            The Address instance with the formatted address string.
        """
        self._formatted = f"{self.street_name} {self.house_nr}"
        if self.suffix:
            self._formatted += f" {self.suffix}"
        self._formatted += f", {self.postcode} {self.city}"
        return self


class NaturalPerson(BaseParty):
    """
    Model for natural person parties in the PactDesk system.

    This class represents an individual person who can be a party to a contract,
    with personal information such as name, address, and date of birth.

    Attributes
    ----------
        party_type: The type of party, fixed to "natural_person".
        full_name: The complete name of the person.
        address: The person's address.
        date_of_birth: The person's date of birth.
        place_of_birth: The person's place of birth.
        country_of_birth: The person's country of birth.
        information_role: Optional role regarding confidential information in NDAs.
    """

    party_type: Literal["natural_person"] = PartyType.NATURAL_PERSON.value
    full_name: str
    address: Address
    date_of_birth: str
    place_of_birth: str
    country_of_birth: str
    information_role: InformationRole | None = None


class LegalEntity(BaseParty):
    """
    Model for legal entity parties in the PactDesk system.

    This class represents a company, organization, or other legal entity that can
    be a party to a contract, with information such as name, registration details,
    and address.

    Attributes
    ----------
        party_type: The type of party, fixed to "legal_entity".
        company_type: The type of legal entity (e.g., LLC, BV, NV).
        name: The name of the legal entity.
        registered_address: The registered address of the legal entity.
        country_of_incorporation: The country where the legal entity is incorporated.
        kvk_nr: The Chamber of Commerce registration number.
        signatory_name: The name of the person authorized to sign on behalf of the entity.
        information_role: Optional role regarding confidential information in NDAs.
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
