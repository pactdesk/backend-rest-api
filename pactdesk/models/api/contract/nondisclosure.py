from typing import Self, TypeVar

from pydantic import Field, model_validator

from pactdesk.models.api.contract.base import BaseContractRequest
from pactdesk.models.domain.enum import ContractType, NdaContractVariant
from pactdesk.models.domain.penalty import Penalty
from pactdesk.models.domain.term import Term


T = TypeVar("T", bound=BaseContractRequest)


class NondisclosureRequest(BaseContractRequest):
    contract_type: ContractType = ContractType.NONDISCLOSURE
    contract_variant: NdaContractVariant = Field(
        default=NdaContractVariant.UNILATERAL_STANDARD,
        description="Specific NDA variant to generate.",
    )
    contract_purpose: str
    penalty_clause: Penalty | None = None
    limited_term: Term | None = None

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_information_roles(self) -> Self:
        for party_key, party in self.parties.items():
            if not party.information_role:
                err_msg = f"Information role must be set for party '{party_key}' in an NDA contract"
                raise ValueError(err_msg)

        if self.contract_variant in [
            NdaContractVariant.UNILATERAL_STANDARD,
            NdaContractVariant.UNILATERAL_MULTI,
        ]:
            disclosing_count = sum(
                party.information_role == "DISCLOSING" for party in self.parties.values()
            )

            if disclosing_count != 1:
                err_msg = "Unilateral NDA's must have exactly one disclosing party"
                raise ValueError(err_msg)

        return self
