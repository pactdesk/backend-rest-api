"""
Base domain models for the PactDesk system.

This module defines the foundational domain models that represent the structure
of contract documents in the PactDesk system. It provides classes for text elements,
paragraphs, clauses, sections, and signatures, along with rendering capabilities
for template-based content generation.
"""

from typing import Any, Self, cast

from jinja2 import Template
from pydantic import BaseModel


class BaseText(BaseModel):
    """
    Base model for text content in contract documents.

    This class serves as the foundation for all text-based elements in contract
    documents, providing basic content storage and rendering capabilities.

    Attributes
    ----------
        content: The text content of the element, which may contain template
            variables for rendering.
    """

    content: str

    def render(self, context: dict[str, str]) -> Self:
        """
        Render the text content using the provided context.

        This method processes the content as a Jinja2 template, replacing any
        template variables with values from the context dictionary.

        Parameters
        ----------
            context: A dictionary mapping template variable names to their values.

        Returns
        -------
            A new instance of BaseText with the rendered content.
        """
        template = Template(self.content)
        rendered_content = template.render(**context)
        return BaseText(content=rendered_content)


class Paragraph(BaseText):
    """
    Model for paragraph elements in contract documents.

    This class extends BaseText to represent paragraphs, which may have a heading
    and contain subparagraphs.

    Attributes
    ----------
        content: The text content of the paragraph.
        heading: Optional heading text for the paragraph.
        subparagraphs: Optional list of subparagraphs contained within this paragraph.
    """

    heading: str | None = None
    subparagraphs: list[BaseText] | None = None

    def render(self, context: dict[str, str]) -> Self:
        """
        Render the paragraph content and its subparagraphs using the provided context.

        This method processes the paragraph content and all its subparagraphs as
        Jinja2 templates, replacing any template variables with values from the
        context dictionary.

        Parameters
        ----------
            context: A dictionary mapping template variable names to their values.

        Returns
        -------
            A new instance of Paragraph with the rendered content and subparagraphs.
        """
        template = Template(self.content)
        rendered_content = template.render(**context)

        rendered_subparagraphs = None
        if self.subparagraphs:
            rendered_subparagraphs = [
                subparagraph.render(context) for subparagraph in self.subparagraphs
            ]

        return Paragraph(content=rendered_content, subparagraphs=rendered_subparagraphs)


class Clause(BaseModel):
    """
    Model for clause elements in contract documents.

    This class represents a clause, which consists of a title and a list of paragraphs.

    Attributes
    ----------
        title: The title of the clause.
        paragraphs: A list of paragraphs contained within this clause.
    """

    title: str
    paragraphs: list[Paragraph]

    def render(self, context: dict[str, str]) -> Self:
        """
        Render the clause title and paragraphs using the provided context.

        This method processes the clause title and all its paragraphs as Jinja2
        templates, replacing any template variables with values from the context
        dictionary.

        Parameters
        ----------
            context: A dictionary mapping template variable names to their values.

        Returns
        -------
            A new instance of Clause with the rendered title and paragraphs.
        """
        title_template = Template(self.title)
        rendered_title = title_template.render(**context)

        return Clause(
            title=rendered_title,
            paragraphs=[paragraph.render(context) for paragraph in self.paragraphs],
        )


class Signature(BaseModel):
    """
    Model for signature elements in contract documents.

    This class represents a signature block in a contract document, which may
    contain fields for party signatures, dates, and other related information.
    """

    pass


class Section(BaseModel):
    """
    Model for section elements in contract documents.

    This class represents a section, which consists of a title, a list of subsections,
    and an optional closing text.

    Attributes
    ----------
        title: The title of the section.
        subsections: A list of subsections contained within this section, which may
            be BaseText, Paragraph, or Clause elements.
        closing: Optional closing text for the section, which may be a BaseText
            object or a string.
    """

    title: str
    subsections: list[BaseText | Paragraph | Clause]
    closing: BaseText | str | None = None

    def render(self, context: dict[str, Any]) -> Self:
        """
        Render the section title, subsections, and closing text using the provided context.

        This method processes the section title, all its subsections, and the closing
        text as Jinja2 templates, replacing any template variables with values from
        the context dictionary. It handles special cases for party-specific rendering
        and global context variables.

        Parameters
        ----------
            context: A dictionary mapping template variable names to their values.

        Returns
        -------
            A new instance of Section with the rendered title, subsections, and closing text.
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

        rendered_closing = None
        if self.closing:
            closing_context = dict(context)
            if "_global" in context and "n_parties" in context["_global"]:
                closing_context["n_parties"] = context["_global"]["n_parties"]
                closing_template = Template(self.closing["content"])
                rendered_closing = closing_template.render(**closing_context)

        return self.__class__(
            title=rendered_title, subsections=rendered_subsections, closing=rendered_closing
        )


class TextSection(Section):
    """
    Model for text-based sections in contract documents.

    This class extends Section to represent sections that contain only text-based
    subsections (BaseText or Paragraph elements).

    Attributes
    ----------
        title: The title of the section.
        subsections: A list of text-based subsections contained within this section.
        closing: Optional closing text for the section.
    """

    @property
    def paragraphs(self) -> list[BaseText]:
        """
        Get the paragraphs contained within this section.

        This property provides access to the subsections as a list of BaseText
        elements, casting the subsections to the appropriate type.

        Returns
        -------
            A list of BaseText elements representing the paragraphs in this section.
        """
        return cast(list[BaseText], self.subsections)

    @classmethod
    def validate_subsections(cls, value: BaseText) -> BaseText:
        """
        Validate that all subsections are of the correct type.

        This method ensures that all subsections in a TextSection are either
        BaseText or Paragraph elements, maintaining the integrity of the section
        structure.

        Parameters
        ----------
            value: A list of subsections to validate.

        Returns
        -------
            The validated list of subsections.

        Raises
        ------
            ValueError: If any subsection is not a BaseText or Paragraph element.
        """
        for item in value:
            if not isinstance(item, BaseText | Paragraph):
                err_msg = (
                    f"TextSection requires BaseText or Paragraph subsections, got {type(item)}"
                )
                raise ValueError(err_msg)

        return value


class ClauseSection(Section):
    """
    Model for clause-based sections in contract documents.

    This class extends Section to represent sections that contain only clause-based
    subsections (Clause elements).

    Attributes
    ----------
        title: The title of the section.
        subsections: A list of clause-based subsections contained within this section.
        closing: Optional closing text for the section.
    """

    @property
    def clauses(self) -> list[Clause]:
        """
        Get the clauses contained within this section.

        This property provides access to the subsections as a list of Clause
        elements, casting the subsections to the appropriate type.

        Returns
        -------
            A list of Clause elements representing the clauses in this section.
        """
        return cast(list[Clause], self.subsections)

    @classmethod
    def validate_subsections(cls, value: Clause) -> Clause:
        """
        Validate that all subsections are of the correct type.

        This method ensures that all subsections in a ClauseSection are Clause
        elements, maintaining the integrity of the section structure.

        Parameters
        ----------
            value: A list of subsections to validate.

        Returns
        -------
            The validated list of subsections.

        Raises
        ------
            ValueError: If any subsection is not a Clause element.
        """
        for item in value:
            if not isinstance(item, Clause):
                err_msg = f"ClauseSection requires Clause subsections, got {type(item)}"
                raise ValueError(err_msg)

        return value
