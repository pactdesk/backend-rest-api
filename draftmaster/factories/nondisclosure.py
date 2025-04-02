from pathlib import Path
from typing import Any

from draftmaster.models.api.contract.nondisclosure import NondisclosureRequest
from draftmaster.models.domain.base import BaseText, Clause, Paragraph, Section
from draftmaster.models.domain.contract import Contract
from draftmaster.models.domain.enum import PartyType
from draftmaster.services import ContextService, TemplateService


class NondisclosureFactory:
    def __init__(
        self,
        request: NondisclosureRequest,
        base_path: Path | None = None,
    ) -> None:
        self.request = request
        self.variant, self.parties = request.contract_variant.split("/")
        self.base_path = base_path

        self.context_service = ContextService()
        self.template_service = TemplateService()

        self.context = self.context_service.construct_context(request)
        self.party_context = self.context_service.construct_party_context(request)

        self.general_path = base_path / "general"
        self.contract_path = base_path / request.contract_type.value
        self.variant_path = self.contract_path / self.variant / self.parties

        self.standard_clauses: list[str] = [
            "definitions",
            "nonuse_and_nondisclosure",
            "use_and_treatment_of",
            "data_privacy",
            "rights_to",
            "return_or_destruction_of",
            "third_party_stipulation",
            "no_warranty",
            "information_receiving_party",
            "miscellaneous",
        ]

    def _load_template(self, *path_parts: str) -> dict[str, Any]:
        return self.template_service.load(Path(*path_parts))

    def _create_section(self, section_name: str, subsections: list[Any]) -> Section:
        section_template = self._load_template(
            self.general_path, "sections", f"{section_name}.json"
        )
        section_template["subsections"] = subsections
        return Section(**section_template)

    def _generate_parties(self) -> Section:
        party_context = self.context_service.construct_party_context(self.request)

        subsections = [
            self.template_service.load_legal_entity()
            if party_context[party]["type"] == PartyType.LEGAL_ENTITY.value
            else self.template_service.load_natural_person()
            for party in party_context.keys()
        ]

        section = self._create_section("parties", subsections)
        section.closing = self._load_template(self.variant_path, "parties", "closing.json")

        return section

    def _generate_considerations(self) -> Section:
        considerations_data = self._load_template(
            self.variant_path, "considerations", "considerations.json"
        )

        paragraphs = []
        if "paragraphs" in considerations_data:
            for paragraph in considerations_data["paragraphs"]:
                if isinstance(paragraph, dict):
                    if "heading" in paragraph or "subparagraphs" in paragraph:
                        paragraphs.append(Paragraph(**paragraph))
                    else:
                        paragraphs.append(BaseText(**paragraph))
                else:
                    paragraphs.append(paragraph)

        return self._create_section("considerations", paragraphs)

    def _generate_agreements(self) -> Section:
        agreements_path = self.variant_path / "agreements"
        clauses_path = agreements_path / "clauses"

        clauses = [
            Clause(**self._load_template(clauses_path, f"{clause}.json"))
            for clause in self.standard_clauses
        ]

        term_type = "limited" if self.request.limited_term else "unlimited"
        term_clause = Clause(**self._load_template(agreements_path, "term", f"{term_type}.json"))

        if self.request.penalty_clause:
            enforcement_path = self.contract_path / "general" / "agreements" / "clauses"
            enforcement_clause = Clause(
                **self._load_template(enforcement_path, "enforcement_and_penalties.json")
            )
        else:
            enforcement_clause = Clause(
                **self._load_template(clauses_path, "enforcement_and_remedies.json")
            )

        no_warranty_index = next(
            i for i, clause in enumerate(clauses) if clause.title.lower().startswith("no warranty")
        )
        clauses.insert(no_warranty_index, enforcement_clause)
        clauses.insert(no_warranty_index, term_clause)

        return self._create_section("agreements", clauses)

    def _generate_signatures(self) -> Section:
        return self._create_section("signatures", [])

    def generate(self) -> Contract:
        return Contract(
            parties=self._generate_parties().render(self.party_context),
            considerations=self._generate_considerations().render(self.context),
            agreements=self._generate_agreements().render(self.context),
            signatures=self._generate_signatures().render(self.context),
        )
