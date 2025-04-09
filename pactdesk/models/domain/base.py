"""Module containing base classes for contract document structure and rendering.

This module provides the foundational classes for building and rendering contract documents.
It includes classes for text elements, paragraphs, clauses, sections, and signatures, with
support for template-based rendering using Jinja2.
"""

from typing import Any, Self, cast

from jinja2 import Template
from pydantic import BaseModel


class BaseText(BaseModel):
    """Base class for text elements in a contract document.

    This class serves as the foundation for all text-based elements in a contract,
    providing basic rendering functionality using Jinja2 templates.

    Attributes:
        content (str): The text content that may contain Jinja2 template variables.
    """

    content: str

    def render(self, context: dict[str, Any]) -> Self:
        """Render the text content using the provided context.

        Args:
            context (dict[str, Any]): Dictionary containing values for template variables.

        Returns:
            Self: A new instance with rendered content.
        """
        template = Template(self.content)
        rendered_content = template.render(**context)
        return self.__class__(content=rendered_content)


class Paragraph(BaseText):
    """Represents a paragraph in a contract document.

    A paragraph can have an optional heading and may contain subparagraphs. It extends
    BaseText to support hierarchical text structure.

    Attributes:
        heading (str | None): Optional heading for the paragraph.
        subparagraphs (list[BaseText] | None): Optional list of subparagraphs.
    """

    heading: str | None = None
    subparagraphs: list[BaseText] | None = None

    def render(self, context: dict[str, Any]) -> Self:
        """Render the paragraph content and its subparagraphs using the provided context.

        Args:
            context (dict[str, Any]): Dictionary containing values for template variables.

        Returns:
            Self: A new instance with rendered content.
        """
        template = Template(self.content)
        rendered_content = template.render(**context)
        return self.__class__(content=rendered_content)


class Clause(BaseText):
    """Represents a clause in a contract document.

    A clause is a structured text element with a title and multiple paragraphs. It
    extends BaseText to support complex contractual provisions.

    Attributes:
        title (str): The title of the clause.
        paragraphs (list[Paragraph]): List of paragraphs within the clause.
    """

    title: str
    paragraphs: list[Paragraph]

    def render(self, context: dict[str, Any]) -> Self:
        """Render the clause title, content, and paragraphs using the provided context.

        Args:
            context (dict[str, Any]): Dictionary containing values for template variables.

        Returns:
            Self: A new instance with rendered title, content, and paragraphs.
        """
        title_template = Template(self.title)
        rendered_title = title_template.render(**context)

        content_template = Template(self.content)
        rendered_content = content_template.render(**context)

        rendered_paragraphs = [paragraph.render(context) for paragraph in self.paragraphs]

        return self.__class__(
            title=rendered_title, content=rendered_content, paragraphs=rendered_paragraphs
        )


class Signature(BaseModel):
    """Represents a signature block in a contract document.

    A signature block contains the name of the signatory and an optional date.

    Attributes:
        name (str): The name of the signatory.
        date (str | None): Optional date of signing.
    """

    name: str
    date: str | None = None

    def render(self, context: dict[str, Any]) -> Self:
        """Render the signature name using the provided context.

        Args:
            context (dict[str, Any]): Dictionary containing values for template variables.

        Returns:
            Self: A new instance with rendered name.
        """
        template = Template(self.name)
        rendered_name = template.render(**context)
        return self.__class__(name=rendered_name, date=self.date)


class Section(BaseModel):
    """Represents a section in a contract document.

    A section is a container that groups related text elements together within a contract.
    It can contain various types of subsections and may include an optional closing
    statement.

    Attributes:
        title (str): The title of the section.
        subsections (list[BaseText | Paragraph | Clause]): List of subsections.
        closing (BaseText | str | None): Optional closing statement.
    """

    title: str
    subsections: list[BaseText | Paragraph | Clause]
    closing: BaseText | str | None = None

    def render(self, context: dict[str, Any]) -> Self:
        """Render the section title, subsections, and closing using the provided context.

        Args:
            context (dict[str, Any]): Dictionary containing values for template variables.

        Returns:
            Self: A new instance with rendered title, subsections, and closing.
        """
        title_template = Template(self.title)
        rendered_title = title_template.render(**context)

        if party_keys := [key for key in context if key.startswith("party_")]:
            rendered_subsections: list[BaseText | Paragraph | Clause] = []
            rendered_subsections.extend(
                subsection.render(context[party_keys[i]])
                for i, subsection in enumerate(self.subsections)
                if i < len(party_keys)
            )
        else:
            rendered_subsections = [subsection.render(context) for subsection in self.subsections]

        rendered_closing: BaseText | str | None = None
        if self.closing:
            closing_context = dict(context)
            if "_global" in context and "n_parties" in context["_global"]:
                closing_context["n_parties"] = context["_global"]["n_parties"]
                if isinstance(self.closing, BaseText):
                    closing_template = Template(self.closing.content)
                    rendered_closing = self.closing.__class__(
                        content=closing_template.render(**closing_context)
                    )

                else:
                    closing_template = Template(self.closing)
                    rendered_closing = closing_template.render(**closing_context)

        return self.__class__(
            title=rendered_title, subsections=rendered_subsections, closing=rendered_closing
        )


class TextSection(Section):
    """Represents a section containing only text elements.

    This class extends Section to enforce that all subsections must be BaseText or
    Paragraph instances.

    Attributes:
        paragraphs (list[BaseText]): List of text paragraphs in the section.
    """

    @property
    def paragraphs(self) -> list[BaseText]:
        """Get the list of paragraphs in the section.

        Returns:
            list[BaseText]: List of text paragraphs.
        """
        return cast(list[BaseText], self.subsections)

    @classmethod
    def validate_subsections(cls, value: BaseText) -> BaseText:
        """Validate that all subsections are BaseText or Paragraph instances.

        Args:
            value (BaseText): The subsections to validate.

        Returns:
            BaseText: The validated subsections.

        Raises:
            ValueError: If any subsection is not a BaseText or Paragraph instance.
        """
        for item in value:
            if not isinstance(item, BaseText | Paragraph):
                err_msg = (
                    f"TextSection requires BaseText or Paragraph subsections, got {type(item)}"
                )
                raise ValueError(err_msg)

        return value


class ClauseSection(Section):
    """Represents a section containing only clause elements.

    This class extends Section to enforce that all subsections must be Clause instances.

    Attributes:
        clauses (list[Clause]): List of clauses in the section.
    """

    @property
    def clauses(self) -> list[Clause]:
        """Get the list of clauses in the section.

        Returns:
            list[Clause]: List of clauses.
        """
        return cast(list[Clause], self.subsections)

    @classmethod
    def validate_subsections(cls, value: Clause) -> Clause:
        """Validate that all subsections are Clause instances.

        Args:
            value (Clause): The subsections to validate.

        Returns:
            Clause: The validated subsections.

        Raises:
            ValueError: If any subsection is not a Clause instance.
        """
        for item in value:
            if not isinstance(item, Clause):
                err_msg = f"ClauseSection requires Clause subsections, got {type(item)}"
                raise ValueError(err_msg)

        return value
