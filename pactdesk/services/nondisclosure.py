"""Module for handling nondisclosure agreement generation.

This module provides services for generating nondisclosure agreements (NDA's) from
templates and request data. It handles the construction of all sections of an NDA,
including parties, considerations, agreements, and signatures.
"""

from pathlib import Path

from loguru import logger

from pactdesk.models.api.contract.nondisclosure import NondisclosureRequest
from pactdesk.models.domain.base import BaseText, Clause, Paragraph, Section
from pactdesk.models.domain.contract import Contract
from pactdesk.models.domain.enum import PartyType
from pactdesk.services.context import ContextService
from pactdesk.services.template import TemplateService


class NondisclosureService:
    """Service for generating non-disclosure agreements.

    This class handles the complete process of generating an NDA from a request,
    including loading templates, constructing sections, and rendering the final
    document.

    Attributes
    ----------
        request (NondisclosureRequest): The NDA generation request.
        variant (str): The NDA variant (unilateral or mutual).
        parties (str): The parties configuration (standard or multi).
        base_path (Path): The base directory for template files.
        context_service (ContextService): Service for constructing context data.
        template_service (TemplateService): Service for loading templates.
        context (dict[str, str | int | None] | None): The general context data.
        party_context (dict[str, dict[str, str | int | None]]): The party context data.
        general_path (Path): Path to general templates.
        contract_path (Path): Path to contract-specific templates.
        variant_path (Path): Path to variant-specific templates.
        standard_clauses (list[str]): List of standard clause names.
    """

    def __init__(
        self,
        request: NondisclosureRequest,
        base_path: Path = Path("templates"),
    ) -> None:
        """Initialize the NDA service with a request and template path.

        Args:
            request (NondisclosureRequest): The NDA generation request.
            base_path (Path): The base directory for template files.
        """
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
        """Create a section with the given name and subsections.

        Args:
            section_name (str): The name of the section to create.
            subsections (list[BaseText | Paragraph | Clause]): The section's content.

        Returns
        -------
            Section: The created section.
        """
        section_template = self.template_service.load(
            self.general_path / "sections" / f"{section_name}.json"
        )
        typed_subsections: list[BaseText | Paragraph | Clause] = list(subsections)
        section_template["subsections"] = typed_subsections
        return Section(**section_template)

    def _generate_parties(self) -> Section:
        """Generate the parties section of the NDA.

        This method creates a section containing information about all parties
        involved in the NDA, including their roles and contact details.

        Returns
        -------
            Section: The generated parties section.
        """
        party_context = self.context_service.construct_party_context(self.request)

        party_keys = [key for key in party_context if key != "_global"]
        subsections: list[BaseText] = [
            self.template_service.load_legal_entity().render(party_context[party])
            if party_context[party]["type"] == PartyType.LEGAL_ENTITY.value
            else self.template_service.load_natural_person().render(party_context[party])
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
        """Generate the considerations section of the NDA.

        This method creates a section describing the considerations exchanged
        between the parties in the NDA.

        Returns
        -------
            Section: The generated considerations section.
        """
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
        """Generate the agreements section of the NDA.

        This method creates a section containing all the clauses that make up
        the main body of the NDA, including standard clauses and any additional
        terms or penalties.

        Returns
        -------
            Section: The generated agreements section.

        Raises
        ------
            Exception: If there is an error loading any clause.
        """
        agreements_path = self.variant_path / "agreements"
        clauses_path = agreements_path / "clauses"

        clauses: list[Clause] = []
        for clause in self.standard_clauses:
            try:
                clause_data = self.template_service.load(clauses_path / f"{clause}.json")
                clauses.append(Clause(**clause_data))

            except Exception as err:
                logger.error(f"Error loading clause {clause}: {err!s}")
                raise

        term_type = "limited" if self.request.limited_term else "unlimited"
        term_clause = Clause(
            **self.template_service.load(agreements_path / "term" / f"{term_type}.json")
        )

        if self.request.penalty_clause:
            enforcement_clause = Clause(
                **self.template_service.load(clauses_path / "enforcement_and_penalties.json")
            )
        else:
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
        """Generate the signatures section of the NDA.

        This method creates a section containing signature blocks for all parties
        to sign the NDA.

        Returns
        -------
            Section: The generated signatures section.
        """
        return self._create_section("signatures", [])

    def generate(self) -> Contract:
        """Generate a complete NDA from the request.

        This method orchestrates the generation of all sections of the NDA and
        combines them into a complete contract document.

        Returns
        -------
            Contract: The generated NDA contract.

        Raises
        ------
            ValueError: If the context or party context is missing.
        """
        if not self.context or not self.party_context:
            err_msg = "Context or party context is missing"
            raise ValueError(err_msg)

        return Contract(
            parties=self._generate_parties(),
            considerations=self._generate_considerations().render(self.context),
            agreements=self._generate_agreements().render(self.context),
            signatures=self._generate_signatures().render(self.context),
        )
