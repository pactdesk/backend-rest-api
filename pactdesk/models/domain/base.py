from typing import Any, Self, cast

from jinja2 import Template
from pydantic import BaseModel


class BaseText(BaseModel):
    content: str

    def render(self, context: dict[str, str]) -> Self:
        template = Template(self.content)
        rendered_content = template.render(**context)
        return self.__class__(content=rendered_content)


class Paragraph(BaseText):
    heading: str | None = None
    subparagraphs: list[BaseText] | None = None

    def render(self, context: dict[str, str]) -> Self:
        rendered_content = super().render(context).content
        rendered_heading = None
        if self.heading:
            heading_template = Template(self.heading)
            rendered_heading = heading_template.render(**context)

        rendered_subparagraphs = None
        if self.subparagraphs:
            rendered_subparagraphs = [
                subparagraph.render(context) for subparagraph in self.subparagraphs
            ]

        return self.__class__(
            content=rendered_content,
            heading=rendered_heading,
            subparagraphs=rendered_subparagraphs,
        )


class Clause(BaseModel):
    title: str
    paragraphs: list[Paragraph]

    def render(self, context: dict[str, str]) -> Self:
        rendered_title = self.title
        if "{{" in self.title or "{%" in self.title:
            title_template = Template(self.title)
            rendered_title = title_template.render(**context)

        rendered_paragraphs = [paragraph.render(context) for paragraph in self.paragraphs]

        return self.__class__(title=rendered_title, paragraphs=rendered_paragraphs)


class Signature(BaseModel):
    pass


class Section(BaseModel):
    title: str
    subsections: list[BaseText | Paragraph | Clause]
    closing: BaseText | str | None = None

    def render(self, context: dict[str, Any]) -> Self:
        title_template = Template(self.title)
        rendered_title = title_template.render(**context)

        rendered_subsections = []
        for subsection in self.subsections:
            if (
                isinstance(subsection, BaseText)
                or isinstance(subsection, Paragraph)
                or isinstance(subsection, Clause)
            ):
                rendered_subsections.append(subsection.render(context))

        rendered_closing = None
        if self.closing:
            closing_context = dict(context)
            if "_global" in context and "n_parties" in context["_global"]:
                closing_context["n_parties"] = context["_global"]["n_parties"]
                if isinstance(self.closing, BaseText):
                    closing_template = Template(self.closing.content)
                    rendered_closing = closing_template.render(**closing_context)
                else:
                    # Handle the case where closing is a string
                    closing_template = Template(self.closing)
                    rendered_closing = closing_template.render(**closing_context)

        return self.__class__(
            title=rendered_title, subsections=rendered_subsections, closing=rendered_closing
        )


class TextSection(Section):
    @property
    def paragraphs(self) -> list[BaseText]:
        return cast(list[BaseText], self.subsections)

    @classmethod
    def validate_subsections(cls, value: BaseText) -> BaseText:
        for item in value:
            if not isinstance(item, BaseText | Paragraph):
                err_msg = (
                    f"TextSection requires BaseText or Paragraph subsections, got {type(item)}"
                )
                raise ValueError(err_msg)

        return value


class ClauseSection(Section):
    @property
    def clauses(self) -> list[Clause]:
        return cast(list[Clause], self.subsections)

    @classmethod
    def validate_subsections(cls, value: Clause) -> Clause:
        for item in value:
            if not isinstance(item, Clause):
                err_msg = f"ClauseSection requires Clause subsections, got {type(item)}"
                raise ValueError(err_msg)

        return value
