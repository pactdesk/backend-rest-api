"""Define contract document models.

This module defines the core contract model that represents the structure of
legal contracts in the PactDesk system. It provides a standardized representation
of contracts with sections for parties, considerations, agreements, and signatures.
"""

from typing import Any, cast

from pydantic import BaseModel, Field


class Contract(BaseModel):
    """Represent a complete legal contract.

    This class represents a complete legal contract document, composed of
    multiple sections including parties, considerations, agreements, and
    signatures.

    Attributes
    ----------
        parties (str): The parties section of the contract.
        considerations (str): The considerations section of the contract.
        agreements (str): The main body of the contract containing all clauses.
        signatures (str): The signatures section of the contract.
    """

    parties: str = Field(..., description="The parties section of the contract")
    considerations: str = Field(..., description="The considerations section of the contract")
    agreements: str = Field(..., description="The main body of the contract containing all clauses")
    signatures: str = Field(..., description="The signatures section of the contract")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Convert the contract model to a dictionary.

        This method overrides the default model_dump to ensure consistent
        serialization of the contract model.

        Args:
            **kwargs: Additional arguments to pass to the base model_dump method.

        Returns
        -------
            dict[str, Any]: The contract model as a dictionary.
        """
        return cast(dict[str, Any], super().model_dump(**kwargs))
