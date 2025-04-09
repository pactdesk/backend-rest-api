"""Module containing base classes for contract document structure and rendering.

This module provides the foundational classes for building and rendering contract documents.
It includes classes for text elements, paragraphs, clauses, sections, and signatures, with
support for template-based rendering using Jinja2.
"""

from typing import Any

from pydantic import BaseModel, Field


class BaseText(BaseModel):
    """Base model for text elements in contract documents.

    This class serves as the foundation for all text-based elements in contract
    documents, providing a consistent structure for content and rendering.

    Attributes
    ----------
        content (str): The text content of the element.
    """

    content: str = Field(..., description="The text content of the element")

    def render(self, context: dict[str, Any] | None = None) -> str:
        """Render the text content with the given context.

        This method formats the text content using the provided context data,
        replacing placeholders with actual values.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            Self: A new instance with rendered content.
        """
        if not context:
            return self.content

        return self.content.format(**context)


class Paragraph(BaseText):
    """Model for paragraphs in contract documents.

    This class represents a paragraph in a contract document, which may include
    a heading and subparagraphs in addition to the main content.

    Attributes
    ----------
        heading (str | None): Optional heading for the paragraph.
        subparagraphs (list[BaseText] | None): Optional list of subparagraphs.
    """

    heading: str | None = Field(None, description="Optional heading for the paragraph")
    subparagraphs: list[str] | None = Field(None, description="Optional list of subparagraphs")

    def render(self, context: dict[str, Any] | None = None) -> str:
        """Render the paragraph with its heading and subparagraphs.

        This method formats the paragraph content, including any heading and
        subparagraphs, using the provided context data.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            str: The rendered paragraph content.
        """
        rendered_content = super().render(context)

        if self.heading:
            rendered_content = f"{self.heading}\n{rendered_content}"

        if self.subparagraphs:
            subparagraphs = [p.format(**context) if context else p for p in self.subparagraphs]
            rendered_content = f"{rendered_content}\n" + "\n".join(subparagraphs)

        return rendered_content


class Clause(BaseText):
    """Model for clauses in contract documents.

    This class represents a clause in a contract document, which includes a
    title and content, and may include paragraphs.

    Attributes
    ----------
        title (str): The title of the clause.
        paragraphs (list[Paragraph] | None): Optional list of paragraphs.
    """

    title: str = Field(..., description="The title of the clause")
    paragraphs: list[Paragraph] | None = Field(None, description="Optional list of paragraphs")

    def render(self, context: dict[str, Any] | None = None) -> str:
        """Render the clause with its title and paragraphs.

        This method formats the clause content, including its title and any
        paragraphs, using the provided context data.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            str: The rendered clause content.
        """
        rendered_content = super().render(context)

        if self.paragraphs:
            paragraphs = [p.render(context) for p in self.paragraphs]
            rendered_content = f"{rendered_content}\n" + "\n\n".join(paragraphs)

        return rendered_content


class Section(BaseText):
    """Model for sections in contract documents.

    This class represents a section in a contract document, which includes
    content and may include subsections and a closing statement.

    Attributes
    ----------
        subsections (list[BaseText | Paragraph | Clause]): List of subsections.
        closing (BaseText | None): Optional closing statement.
    """

    subsections: list[BaseText | Paragraph | Clause] = Field(
        default_factory=list, description="List of subsections"
    )
    closing: BaseText | None = Field(None, description="Optional closing statement")

    def render(self, context: dict[str, Any] | None = None) -> str:
        """Render the section with its subsections and closing.

        This method formats the section content, including all subsections and
        any closing statement, using the provided context data.

        Args:
            context (dict[str, Any] | None): The context data for rendering.

        Returns
        -------
            str: The rendered section content.
        """
        rendered_content = super().render(context)

        if self.subsections:
            subsections = [s.render(context) for s in self.subsections]
            rendered_content = f"{rendered_content}\n" + "\n\n".join(subsections)

        if self.closing:
            rendered_content = f"{rendered_content}\n{self.closing.render(context)}"

        return rendered_content
