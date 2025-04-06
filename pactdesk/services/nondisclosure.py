"""
Nondisclosure agreement service for the PactDesk system.

This module provides services for generating nondisclosure agreements (NDAs)
based on contract requests. It handles different NDA variants and constructs
complete contract documents with appropriate sections and clauses.
"""

from pathlib import Path
from typing import Any

from pactdesk.models.api.contract.nondisclosure import NondisclosureRequest
from pactdesk.models.domain.base import BaseText, Clause, Paragraph, Section
from pactdesk.models.domain.contract import Contract
from pactdesk.models.domain.enum import NdaContractVariant, PartyType
from pactdesk.services import ContextService, TemplateService


class NondisclosureService:
    """
    Service for generating nondisclosure agreements.

    This class handles the generation of nondisclosure agreements based on
    contract requests. It supports different NDA variants and constructs
    complete contract documents with appropriate sections and clauses.

    Attributes
    ----------
        request: The nondisclosure agreement request containing all necessary information.
        variant: The NDA variant (unilateral or mutual).
        parties: The number of parties involved (standard or multi).
        base_path: The base path for template files.
        context_service: Service for constructing context dictionaries.
        template_service: Service for loading and rendering templates.
        context: The context dictionary for the contract.
        party_context: The context dictionary for party information.
        general_path: Path to general template files.
        contract_path: Path to contract-specific template files.
        variant_path: Path to variant-specific template files.
        standard_clauses: List of standard clause names for NDAs.
    """

    def __init__(
        self,
        request: NondisclosureRequest,
        base_path: Path = Path("templates"),
    ) -> None:
        """
        Initialize the NondisclosureService.

        This method sets up the service with the provided request and base path,
        initializes the context services, and prepares the template paths.

        Parameters
        ----------
            request: The nondisclosure agreement request.
            base_path: The base path for template files, defaults to "templates".
        """
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
            "miscellaneous",
        ]

    def _load_template(self, *path_parts: str) -> dict[str, Any]:
        """
        Load a template file from the specified path.

        This method converts path parts to a Path object and loads the template
        using the template service.

        Parameters
        ----------
            *path_parts: Variable number of path parts to construct the template path.

        Returns
        -------
            The loaded template as a dictionary.
        """
        # Convert path parts to a Path object
        return self.template_service.load(Path(*path_parts))

    def _create_section(self, section_name: str, subsections: list[Any]) -> Section:
        """
        Create a section with the specified name and subsections.

        This method loads a section template and adds the provided subsections
        to create a complete section.

        Parameters
        ----------
            section_name: The name of the section to create.
            subsections: A list of subsections to include in the section.

        Returns
        -------
            A Section object with the specified name and subsections.
        """
        section_template = self._load_template(
            self.general_path, "sections", f"{section_name}.json"
        )
        section_template["subsections"] = subsections
        return Section(**section_template)

    def _generate_parties(self) -> Section:
        """
        Generate the parties section of the NDA.

        This method creates a section containing information about all parties
        involved in the NDA, with appropriate templates for each party type.

        Returns
        -------
            A Section object containing party information.
        """
        party_context = self.context_service.construct_party_context(self.request)

        party_keys = [key for key in party_context if key != "_global"]
        subsections = [
            self.template_service.load_legal_entity()
            if party_context[party]["type"] == PartyType.LEGAL_ENTITY.value
            else self.template_service.load_natural_person()
            for party in party_keys
        ]

        section = self._create_section("parties", subsections)
        section.closing = self._load_template(self.variant_path, "parties", "closing.json")

        return section

    def _generate_considerations(self) -> Section:
        """
        Generate the considerations section of the NDA.

        This method creates a section describing the considerations exchanged
        between parties in the NDA.

        Returns
        -------
            A Section object containing consideration information.
        """
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
        """
        Generate the agreements section of the NDA.

        This method creates a section containing all the clauses of the NDA,
        including standard clauses, term clauses, and enforcement clauses.
        It handles different NDA variants and adds appropriate clauses based
        on the request.

        Returns
        -------
            A Section object containing all agreement clauses.
        """
        agreements_path = self.variant_path / "agreements"
        clauses_path = agreements_path / "clauses"

        clauses = [
            Clause(**self._load_template(clauses_path, f"{clause}.json"))
            for clause in self.standard_clauses
        ]

        term_type = "limited" if self.request.limited_term else "unlimited"
        term_clause = Clause(**self._load_template(agreements_path, "term", f"{term_type}.json"))

        if self.request.penalty_clause:
            enforcement_clause = Clause(
                **self._load_template(clauses_path, "enforcement_and_penalties.json")
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

        if self.request.contract_variant in [
            NdaContractVariant.UNILATERAL_STANDARD,
            NdaContractVariant.UNILATERAL_MULTI,
        ]:
            information_receiving_party_clause = Clause(
                **self._load_template(clauses_path, "information_receiving_party.json")
            )
            clauses.insert(no_warranty_index + 2, information_receiving_party_clause)

        return self._create_section("agreements", clauses)

    def _generate_signatures(self) -> Section:
        """
        Generate the signatures section of the NDA.

        This method creates a section for party signatures in the NDA.

        Returns
        -------
            A Section object for party signatures.
        """
        return self._create_section("signatures", [])

    def generate(self) -> Contract:
        """
        Generate a complete NDA contract.

        This method creates a complete NDA contract by generating all sections
        and rendering them with the appropriate context.

        Returns
        -------
            A Contract object representing the complete NDA.
        """
        return Contract(
            parties=self._generate_parties().render(self.party_context),
            considerations=self._generate_considerations().render(self.context),
            agreements=self._generate_agreements().render(self.context),
            signatures=self._generate_signatures().render(self.context),
        )
