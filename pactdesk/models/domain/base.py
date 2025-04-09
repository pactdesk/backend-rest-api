from typing import Any, Self, cast

from jinja2 import Template
from pydantic import BaseModel


class BaseText(BaseModel):
    content: str

    def render(self, context: dict[str, str]) -> Self:
        template = Template(self.content)
        rendered_content = template.render(**context)
        return BaseText(content=rendered_content)


class Paragraph(BaseText):
    heading: str | None = None
    subparagraphs: list[BaseText] | None = None

    def render(self, context: dict[str, str]) -> Self:
        template = Template(self.content)
        rendered_content = template.render(**context)

        rendered_subparagraphs = None
        if self.subparagraphs:
            rendered_subparagraphs = [
                subparagraph.render(context) for subparagraph in self.subparagraphs
            ]

        return Paragraph(content=rendered_content, subparagraphs=rendered_subparagraphs)


class Clause(BaseModel):
    title: str
    paragraphs: list[Paragraph]

    def render(self, context: dict[str, str]) -> Self:
        title_template = Template(self.title)
        rendered_title = title_template.render(**context)

        return Clause(
            title=rendered_title,
            paragraphs=[paragraph.render(context) for paragraph in self.paragraphs],
        )


class Signature(BaseModel):
    pass


class Section(BaseModel):
    title: str
    subsections: list[BaseText | Paragraph | Clause]
    closing: BaseText | str | None = None

    def render(self, context: dict[str, Any]) -> Self:
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
