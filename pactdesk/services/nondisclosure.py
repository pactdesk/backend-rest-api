from pathlib import Path

from loguru import logger

from pactdesk.models.api.contract.nondisclosure import NondisclosureRequest
from pactdesk.models.domain.base import BaseText, Clause, Paragraph, Section
from pactdesk.models.domain.contract import Contract
from pactdesk.models.domain.enum import PartyType
from pactdesk.services.context import ContextService
from pactdesk.services.template import TemplateService


class NondisclosureService:
    def __init__(
        self,
        request: NondisclosureRequest,
        base_path: Path = Path("templates"),
    ) -> None:
        self.request = request
        self.variant, self.parties = request.contract_variant.split("/")
        self.base_path = base_path

        self.context_service = ContextService()
        self.template_service = TemplateService(base_path=base_path)

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

    def _create_section(
        self, section_name: str, subsections: list[BaseText | Paragraph | Clause]
    ) -> Section:
        section_template = self.template_service.load(
            self.general_path / "sections" / f"{section_name}.json"
        )
        typed_subsections: list[BaseText | Paragraph | Clause] = list(subsections)
        section_template["subsections"] = typed_subsections
        return Section(**section_template)

    def _generate_parties(self) -> Section:
        party_context = self.context_service.construct_party_context(self.request)

        party_keys = [key for key in party_context if key != "_global"]
        subsections: list[BaseText] = [
            self.template_service.load_legal_entity()
            if party_context[party]["type"] == PartyType.LEGAL_ENTITY.value
            else self.template_service.load_natural_person()
            for party in party_keys
        ]

        section = self._create_section("parties", subsections)
        closing_template = self.template_service.load(
            self.variant_path / "parties" / "closing.json"
        )
        section.closing = (
            BaseText(**closing_template) if isinstance(closing_template, dict) else closing_template
        )

        return section

    def _generate_considerations(self) -> Section:
        considerations_data = self.template_service.load(
            self.variant_path / "considerations" / "considerations.json"
        )

        paragraphs: list[BaseText | Paragraph] = []
        if "paragraphs" in considerations_data:
            for paragraph in considerations_data["paragraphs"]:
                if isinstance(paragraph, dict):
                    if "heading" in paragraph or "subparagraphs" in paragraph:
                        paragraphs.append(Paragraph(**paragraph))
                    else:
                        paragraphs.append(BaseText(**paragraph))

                else:
                    paragraphs.append(BaseText(content=str(paragraph)))

        return self._create_section("considerations", paragraphs)

    def _generate_agreements(self) -> Section:
        agreements_path = self.variant_path / "agreements"
        clauses_path = agreements_path / "clauses"

        clauses: list[Clause] = []
        for clause in self.standard_clauses:
            logger.debug(f"Loading clause: {clause}")
            try:
                clause_data = self.template_service.load(clauses_path / f"{clause}.json")
                clauses.append(Clause(**clause_data))

            except Exception as err:
                logger.error(f"Error loading clause {clause}: {err!s}")
                raise

        term_type = "limited" if self.request.limited_term else "unlimited"
        logger.debug(f"Loading term clause: {term_type}")
        term_clause = Clause(
            **self.template_service.load(agreements_path / "term" / f"{term_type}.json")
        )

        if self.request.penalty_clause:
            logger.debug("Loading enforcement_and_penalties.json")
            enforcement_clause = Clause(
                **self.template_service.load(clauses_path / "enforcement_and_penalties.json")
            )
        else:
            logger.debug("Loading enforcement_and_remedies.json")
            enforcement_clause = Clause(
                **self.template_service.load(clauses_path / "enforcement_and_remedies.json")
            )

        no_warranty_index = next(
            i for i, clause in enumerate(clauses) if clause.title.lower().startswith("no warranty")
        )
        clauses.insert(no_warranty_index, enforcement_clause)
        clauses.insert(no_warranty_index, term_clause)

        typed_clauses: list[BaseText | Paragraph | Clause] = list(clauses)
        return self._create_section("agreements", typed_clauses)

    def _generate_signatures(self) -> Section:
        return self._create_section("signatures", [])

    def generate(self) -> Contract:
        if not self.context or not self.party_context:
            err_msg = "Context or party context is missing"
            raise ValueError(err_msg)

        return Contract(
            parties=self._generate_parties().render(self.party_context),
            considerations=self._generate_considerations().render(self.context),
            agreements=self._generate_agreements().render(self.context),
            signatures=self._generate_signatures().render(self.context),
        )
