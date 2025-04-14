"""Module containing base classes for contract document structure and rendering.

This module provides the foundational classes for building and rendering contract documents.
It includes classes for text elements, paragraphs, clauses, sections, and signatures, with
support for template-based rendering using Jinja2.
"""

from typing import Any, Self

from jinja2 import Template
from pydantic import BaseModel, Field, model_validator


class BaseText(BaseModel):
    """Base model for text elements in contract documents.

    This class serves as the foundation for all text-based elements in contract
    documents, providing a consistent structure for content and rendering.

    Attributes
    ----------
        content (str): The text content of the element.
    """

    content: str = Field(..., description="The text content of the element")

    def render(self, context: dict[str, Any] | None = None) -> Self:
        """Render the text content with the given context using Jinja2.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: The instance with rendered content.
        """
        if not context:
            return self

        # Render content using Jinja2 Template
        template = Template(self.content)
        self.content = template.render(**context)

        return self


class Paragraph(BaseText):
    """Model for paragraphs in contract documents.

    This class represents a paragraph in a contract document, which may include
    a heading and subparagraphs in addition to the main content.

    Attributes
    ----------
        heading (str | None): Optional heading for the paragraph.
        subparagraphs (list[BaseText] | None): Optional list of subparagraphs,
            where each subparagraph is a BaseText instance.
    """

    heading: str | None = Field(None, description="Optional heading for the paragraph")
    subparagraphs: list[BaseText] | None = Field(
        None, description="Optional list of BaseText subparagraphs"
    )

    @classmethod
    @model_validator(mode="before")  # type: ignore[misc]
    def preprocess_subparagraphs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Preprocess subparagraphs to handle various input formats.

        This validator handles different formats of subparagraphs found in templates:
        - List of dictionaries with 'content' field
        - List of strings

        Args:
            data (Dict[str, Any]): The raw input data.

        Returns
        -------
            Dict[str, Any]: The processed data.
        """
        if isinstance(data, dict) and "subparagraphs" in data and data["subparagraphs"] is not None:
            processed = []

            for item in data["subparagraphs"]:
                if isinstance(item, BaseText):
                    processed.append(item)

                elif isinstance(item, dict) and "content" in item:
                    processed.append(BaseText(content=item["content"]))

                elif isinstance(item, str):
                    processed.append(BaseText(content=item))

            data["subparagraphs"] = processed

        return data

    def render(self, context: dict[str, Any] | None = None) -> Self:
        """Render the paragraph with its heading and subparagraphs using Jinja2.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: The instance with rendered content.
        """
        if not context:
            return self

        super().render(context)

        if self.heading:
            template = Template(self.heading)
            self.heading = template.render(**context)

        if self.subparagraphs:
            for subparagraph in self.subparagraphs:
                subparagraph.render(context)

        return self


class Clause(BaseModel):
    """Model for clauses in contract documents.

    This class represents a clause in a contract document, which includes a
    title and may include content and paragraphs.

    Attributes
    ----------
        title (str): The title of the clause.
        content (str): The content of the clause.
        paragraphs (list[Paragraph] | None): Optional list of paragraphs.
    """

    title: str = Field(..., description="The title of the clause")
    paragraphs: list[Paragraph] | None = Field(None, description="Optional list of paragraphs")

    def render(self, context: dict[str, Any] | None = None) -> Self:
        """Render the clause with its title, content, and paragraphs using Jinja2.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: The instance with rendered content.
        """
        if not context:
            return self

        title_template = Template(self.title)
        self.title = title_template.render(**context)

        if self.paragraphs:
            for paragraph in self.paragraphs:
                paragraph.render(context)

        return self


class Section(BaseModel):
    """Model for sections in contract documents.

    This class represents a section in a contract document, which includes
    a title and subsections, and may include a closing statement.

    Attributes
    ----------
        title (str): The title of the section.
        subsections (list[BaseText | Paragraph | Clause]): List of subsections.
        closing (BaseText | None): Optional closing statement.
    """

    title: str = Field(..., description="The title of the section")
    subsections: list[BaseText | Paragraph | Clause] = Field(
        default_factory=list, description="List of subsections"
    )
    closing: BaseText | None = Field(None, description="Optional closing statement")

    def render(self, context: dict[str, Any] | None = None) -> Self:
        """Render the section using Jinja2.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: The instance with rendered content.
        """
        if not context:
            return self

        title_template = Template(self.title)
        self.title = title_template.render(**context)

        for subsection in self.subsections:
            if hasattr(subsection, "render") and callable(subsection.render):
                subsection.render(context)

        if self.closing:
            self.closing.render(context)

        return self

    def to_string(self) -> str:
        """Convert the section to a string representation.

        Returns
        -------
            str: The string representation of the section.
        """
        parts = [self.title]

        for subsection in self.subsections:
            if hasattr(subsection, "to_string") and callable(subsection.to_string):
                parts.append(subsection.to_string())

            elif isinstance(subsection, BaseText) or hasattr(subsection, "content"):
                parts.append(subsection.content)

        if self.closing:
            parts.append(self.closing.content)

        return "\n\n".join(parts)
