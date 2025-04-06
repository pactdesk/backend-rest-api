"""
Nondisclosure agreement contract request models for the PactDesk API.

This module defines the specific contract request models for nondisclosure agreements
(NDA's) in the PactDesk system. It extends the base contract request models with
additional fields and validation rules specific to NDA's, such as contract purpose,
penalty clauses, and limited terms.
"""

from typing import Self, TypeVar

from pydantic import Field, model_validator

from pactdesk.models.api.contract.base import BaseContractRequest
from pactdesk.models.domain.enum import ContractType, NdaContractVariant
from pactdesk.models.domain.penalty import Penalty
from pactdesk.models.domain.term import Term


T = TypeVar("T", bound=BaseContractRequest)


class NondisclosureRequest(BaseContractRequest):
    """
    Model for nondisclosure agreement contract requests in the PactDesk system.

    This class extends the base contract request model with fields specific to
    nondisclosure agreements, such as contract variant, purpose, penalty clauses,
    and limited terms. It implements additional validation logic to ensure that
    all parties have information roles assigned and that unilateral NDA's have
    exactly one disclosing party.

    Attributes
    ----------
        contract_type: The type of contract, fixed to NONDISCLOSURE.
        contract_variant: The specific NDA variant to generate, defaults to
            UNILATERAL_STANDARD.
        contract_purpose: A description of the purpose for which the NDA is being
            entered into.
        penalty_clause: Optional penalty clause specifying the consequences of
            breaching the NDA.
        limited_term: Optional term specifying the duration of the NDA.
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
        """
        Validate that all parties have information roles and unilateral NDA's have exactly one
        disclosing party.

        This validator ensures that every party in an NDA contract has an information
        role assigned, which is essential for determining the disclosing and receiving
        parties. For unilateral NDA's, it also verifies that there is exactly one
        disclosing party, maintaining the integrity of the contract.

        Returns
        -------
            The validated NondisclosureRequest instance.

        Raises
        ------
            ValueError: If any party lacks an information role or if a unilateral NDA
                does not have exactly one disclosing party.
        """  # noqa: D205
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
