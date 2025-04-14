"""Define contract document models with Jinja2 rendering support.

This module defines the core contract model that represents the structure of
legal contracts in the PactDesk system, with Jinja2 template rendering.
"""

from typing import Any, Self

from jinja2 import Template
from pydantic import BaseModel, Field


class Contract(BaseModel):
    """Represent a complete legal contract.

    This class represents a complete legal contract document, composed of
    multiple sections including parties, considerations, agreements, and
    signatures.

    Attributes
    ----------
        parties (object): The parties section of the contract.
        considerations (object): The considerations section of the contract.
        agreements (object): The main body of the contract containing all clauses.
        signatures (object): The signatures section of the contract.
    """

    parties: object = Field(..., description="The parties section of the contract")
    considerations: object = Field(..., description="The considerations section of the contract")
    agreements: object = Field(
        ..., description="The main body of the contract containing all clauses"
    )
    signatures: object = Field(..., description="The signatures section of the contract")

    def render(self, context: dict[str, Any] | None = None) -> Self:
        """Render the contract with the given context using Jinja2.

        This method applies the context data to all sections of the contract.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: The instance with rendered content.
        """
        if not context:
            return self

        # Render each section if it has a render method
        if hasattr(self.parties, "render") and callable(self.parties.render):
            self.parties.render(context)
        elif isinstance(self.parties, str):
            template = Template(self.parties)
            self.parties = template.render(**context)

        if hasattr(self.considerations, "render") and callable(self.considerations.render):
            self.considerations.render(context)
        elif isinstance(self.considerations, str):
            template = Template(self.considerations)
            self.considerations = template.render(**context)

        if hasattr(self.agreements, "render") and callable(self.agreements.render):
            self.agreements.render(context)
        elif isinstance(self.agreements, str):
            template = Template(self.agreements)
            self.agreements = template.render(**context)

        if hasattr(self.signatures, "render") and callable(self.signatures.render):
            self.signatures.render(context)
        elif isinstance(self.signatures, str):
            template = Template(self.signatures)
            self.signatures = template.render(**context)

        return self

    def to_string(self) -> str:
        """Convert the contract to a string representation.

        Returns
        -------
            str: The string representation of the contract.
        """
        parts = []

        # Add each section
        for section in [self.parties, self.considerations, self.agreements, self.signatures]:
            if hasattr(section, "to_string") and callable(section.to_string):
                parts.append(section.to_string())
            elif isinstance(section, str):
                parts.append(section)

        return "\n\n".join(parts)
