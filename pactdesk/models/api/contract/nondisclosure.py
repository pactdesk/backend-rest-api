"""Module for handling NDA contract requests.

This module provides the NondisclosureRequest class which represents a request to generate
a non-disclosure agreement. It includes validation for party roles and contract variants,
ensuring the NDA meets specific requirements such as having exactly one disclosing party
for unilateral agreements.
"""

from typing import Self, TypeVar

from pydantic import Field, model_validator

from pactdesk.models.api.contract.base import BaseContractRequest
from pactdesk.models.domain.enum import ContractType, NdaContractVariant
from pactdesk.models.domain.penalty import Penalty
from pactdesk.models.domain.term import Term


T = TypeVar("T", bound="NondisclosureRequest")


class NondisclosureRequest(BaseContractRequest):
    """Represents a request to generate a non-disclosure agreement.

    This class extends BaseContractRequest to handle NDA-specific requirements and
    validations. It ensures proper configuration of parties, contract variants, and
    additional NDA-specific clauses like penalties and term limitations.

    Attributes
    ----------
        contract_type (ContractType): Always set to ContractType.NONDISCLOSURE for NDA
            contracts.
        contract_variant (NdaContractVariant): Specifies the type of NDA (e.g., unilateral,
            mutual).
        contract_purpose (str): Description of the purpose for the NDA.
        penalty_clause (Penalty | None): Optional penalty clause for breach of agreement.
        limited_term (Term | None): Optional term limitation for the agreement.
    """

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
        """Validate the information roles of parties in the NDA.

        This validator ensures all parties have an assigned information role and for
        unilateral NDAs, exactly one party is designated as the disclosing party.

        Returns
        -------
            Self: The validated NondisclosureRequest instance.

        Raises
        ------
            ValueError: If any party lacks an information role or if a unilateral NDA has
                an incorrect number of disclosing parties.
        """
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
