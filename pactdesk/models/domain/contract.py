"""Define contract document models with Jinja2 rendering support.

This module defines the core contract model that represents the structure of
legal contracts in the PactDesk system, with Jinja2 template rendering.
"""

from typing import Any, Self

from pydantic import BaseModel, Field

from pactdesk.models.domain.base import Clause


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

    def _get_sections(self) -> list[object]:
        """Get all sections of the contract in order.

        Returns
        -------
            list[object]: List of all sections in the contract.
        """
        return [self.parties, self.considerations, self.agreements, self.signatures]

    def _process_clause(self, clause: Clause, indices: dict[str, int]) -> None:
        """Process a single clause and add its indices to the dictionary.

        Args:
            clause (Clause): The clause to process.
            indices (dict[str, int]): The dictionary to store indices in.
        """
        if clause.position is None:
            return

        clause_name = clause.title.lower().replace(" ", "_")
        indices[f"{clause_name}_clause_idx"] = clause.position

        if clause.paragraphs:
            for i, _ in enumerate(clause.paragraphs, 1):
                indices[f"{clause_name}_paragraph_{i}"] = i

    def _process_section(self, section: object, indices: dict[str, int]) -> None:
        """Process a single section and add its clause indices to the dictionary.

        Args:
            section (object): The section to process.
            indices (dict[str, int]): The dictionary to store indices in.
        """
        if not hasattr(section, "subsections"):
            return

        for subsection in section.subsections:
            if isinstance(subsection, Clause):
                self._process_clause(subsection, indices)

    def assign_positions(self) -> None:
        """Assign positions to all sections, clauses, and paragraphs in the contract."""
        current_position = 1
        for section in self._get_sections():
            if hasattr(section, "assign_positions"):
                current_position = section.assign_positions(current_position)

    def get_indices(self) -> dict[str, int]:
        """Generate a dictionary of clause and paragraph indices.

        Returns
        -------
            dict[str, int]: A dictionary mapping clause and paragraph names to their indices.
        """
        indices: dict[str, int] = {}
        for section in self._get_sections():
            self._process_section(section, indices)
        return indices

    def render(self, context: dict[str, Any] | None = None) -> Self:
        """Render the contract with the given context.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: The instance with rendered content.
        """
        if not context:
            return self

        # First assign positions to all elements
        self.assign_positions()

        # Get clause and paragraph indices
        indices = self.get_indices()

        # Merge indices with the provided context
        full_context = {**context, **indices}

        # Render each section with the full context
        for section in self._get_sections():
            if hasattr(section, "render"):
                section.render(full_context)

        return self

    def to_string(self) -> str:
        """Convert the contract to a string representation.

        Returns
        -------
            str: The string representation of the contract.
        """
        parts = []

        # Add each section
        for section in self._get_sections():
            if hasattr(section, "to_string") and callable(section.to_string):
                parts.append(section.to_string())
            elif isinstance(section, str):
                parts.append(section)

        return "\n\n".join(parts)
