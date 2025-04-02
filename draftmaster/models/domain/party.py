from datetime import date
import re
from typing import Annotated, Literal, Self, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from draftmaster.models.domain.enum import CompanyType, InformationRole, PartyType


class BaseParty(BaseModel):
    party_type: str
    name: str


class Address(BaseModel):
    street_name: str
    house_nr: int
    city: str
    postcode: str
    suffix: str | None = None
    _formatted: str | None = None

    @field_validator("postcode")
    @classmethod
    def validate_postcode(cls, v: str) -> str:
        pattern = r"^[0-9]{4}([ ]?)[A-Z]{2}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Postcode must be 4 digits followed by 2 capital letters (with or without a space)"
            )

        return v

    @model_validator(mode="after")
    def format_address(self) -> Self:
        self._formatted = (
            f"{self.street_name} {self.house_nr}"
            f"{self.suffix or ''}"
            f", ({self.postcode}), {self.city}"
        )

        return self


class NaturalPerson(BaseParty):
    party_type: Literal["natural_person"] = PartyType.NATURAL_PERSON.value
    full_name: str
    address: Address
    date_of_birth: date
    city_of_birth: str
    country_of_birth: str
    information_role: InformationRole | None = None


class LegalEntity(BaseParty):
    party_type: Literal["legal_entity"] = PartyType.LEGAL_ENTITY.value
    company_type: CompanyType
    name: str
    registered_address: Address
    country_of_incorporation: str
    kvk_nr: str
    signatory_name: str
    information_role: InformationRole | None = None


Party = Annotated[Union[NaturalPerson, LegalEntity], Field(discriminator="party_type")]
