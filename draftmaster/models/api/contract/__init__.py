from typing import Annotated, Union

from pydantic import Field

from draftmaster.models.api.contract.base import BaseContractRequest
from draftmaster.models.api.contract.nondisclosure import NondisclosureRequest


ContractRequest = Annotated[Union[NondisclosureRequest], Field(discriminator="contract_type")]

__all__ = [
    "BaseContractRequest",
    "NondisclosureRequest",
    "ContractRequest",
]
