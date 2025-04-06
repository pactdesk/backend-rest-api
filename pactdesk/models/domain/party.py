import re
from typing import Annotated, Literal, Self, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

from pactdesk.models.domain.enum import CompanyType, InformationRole, PartyType


T = TypeVar("T", bound=BaseModel)


class BaseParty(BaseModel):
    party_type: str


class Address(BaseModel):
    street_name: str
    house_nr: str
    city: str
    postcode: str
    suffix: str | None = None
    _formatted: str | None = None

    @field_validator("postcode")  # type: ignore[misc]
    @classmethod
    def validate_postcode(cls: type[T], value: str) -> str:
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
        self._formatted = f"{self.street_name} {self.house_nr}"
        if self.suffix:
            self._formatted += f" {self.suffix}"
        self._formatted += f", {self.postcode} {self.city}"
        return self


class NaturalPerson(BaseParty):
    party_type: Literal["natural_person"] = PartyType.NATURAL_PERSON.value
    full_name: str
    address: Address
    date_of_birth: str
    place_of_birth: str
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


Party = Annotated[NaturalPerson | LegalEntity, Field(discriminator="party_type")]
