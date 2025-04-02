from pydantic import BaseModel, field_validator

from draftmaster.models.domain.party import Party


class BaseContractRequest(BaseModel):
    contract_type: str
    parties: dict[str, Party]
    applicable_law: str
    place_of_jurisdiction: str

    @field_validator("parties")
    @classmethod
    def validate_parties(cls, v):
        if len(v) < 2:
            raise ValueError("At least two parties are required for contract generation.")

        return v
