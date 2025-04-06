from typing import Annotated

from pydantic import Field

from pactdesk.models.api.contract.base import BaseContractRequest
from pactdesk.models.api.contract.nondisclosure import NondisclosureRequest


ContractRequest = Annotated[NondisclosureRequest, Field(discriminator="contract_type")]

__all__ = [
    "BaseContractRequest",
    "NondisclosureRequest",
    "ContractRequest",
]
