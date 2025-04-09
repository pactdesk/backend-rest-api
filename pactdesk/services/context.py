"""Module for handling context construction in contract generation.

This module provides services for constructing the context data needed for
rendering contract templates. It handles different types of contracts and
their specific context requirements.
"""

from loguru import logger
from pydantic import BaseModel

from pactdesk.models.api.contract import ContractRequest
from pactdesk.models.domain.enum import ContractType, InformationRole, PartyType
from pactdesk.models.domain.party import LegalEntity, NaturalPerson


class ContextService(BaseModel):
    """Service for constructing context data for contract templates.

    This class provides methods for building the context data needed to render
    contract templates, including party-specific and contract-type-specific
    information.
    """

    @staticmethod
    def construct_party_context(request: ContractRequest) -> dict[str, dict[str, str | int | None]]:
        """Construct the context data for contract parties.

        This method builds a dictionary containing all party-specific information
        needed for template rendering, including roles and contact details.

        Args:
            request (ContractRequest): The contract request containing party data.

        Returns
        -------
            dict[str, dict[str, str | int | None]]: The constructed party context.

        Raises
        ------
            ValueError: If an invalid party type is encountered.
        """
        total_parties = len(request.parties)
        party_context: dict[str, dict[str, str | int | None]] = {
            "_global": {
                "n_parties": str(total_parties),
                "contract_variant": request.contract_variant.value,
            }
        }

        for key, party in request.parties.items():
            if total_parties == 2:
                role = (
                    "the Disclosing Party"
                    if party.information_role == InformationRole.DISCLOSING
                    else "the Receiving Party"
                )
            else:
                role = party.name if isinstance(party, LegalEntity) else party.full_name

            if isinstance(party, LegalEntity):
                party_context[key] = {
                    "type": PartyType.LEGAL_ENTITY.value,
                    "name": party.name,
                    "company_type": party.company_type.value,
                    "country": party.country_of_incorporation,
                    "address": party.registered_address._formatted,
                    "kvk_nr": party.kvk_nr,
                    "representative": party.signatory_name,
                    "role": role,
                }
            elif isinstance(party, NaturalPerson):
                party_context[key] = {
                    "type": PartyType.NATURAL_PERSON.value,
                    "name": party.full_name,
                    "date_of_birth": party.date_of_birth,
                    "place_of_birth": party.place_of_birth,
                    "address": party.address._formatted,
                    "role": role,
                }

            else:
                err_msg = (
                    f"Party type {party.party_type} is not valid. "
                    "Must be either `legal_entity` or `natural_person`."
                )
                raise ValueError(err_msg)

        return party_context

    @staticmethod
    def _construct_nondisclosure_context(request: ContractRequest) -> dict[str, str | int | None]:
        """Construct the context data for non-disclosure agreements.

        This method builds a dictionary containing all NDA-specific information
        needed for template rendering, including purpose and term details.

        Args:
            request (ContractRequest): The NDA contract request.

        Returns
        -------
            dict[str, str | int | None]: The constructed NDA context.
        """
        context: dict[str, str | int | None] = {
            "city": request.place_of_jurisdiction,
            "country": request.applicable_law,
            "purpose": request.contract_purpose,
        }

        if request.limited_term:
            context.update(
                {
                    "duration_amount": str(request.limited_term.duration_amount),
                    "duration_unit": request.limited_term.duration_unit,
                }
            )

        if request.penalty_clause:
            context.update(
                {
                    "initial_amount": str(request.penalty_clause.initial_amount),
                    "subsequent_amount": str(request.penalty_clause.subsequent_amount),
                }
            )

        return context

    @staticmethod
    def _construct_shareholder_context(request: ContractRequest) -> dict[str, str | int | None]:
        """Construct the context data for shareholder agreements.

        Args:
            request (ContractRequest): The shareholder agreement request.

        Returns
        -------
            dict[str, str | int | None]: The constructed shareholder context.
        """
        return {}

    @staticmethod
    def _construct_management_context(request: ContractRequest) -> dict[str, str | int | None]:
        """Construct the context data for management agreements.

        Args:
            request (ContractRequest): The management agreement request.

        Returns
        -------
            dict[str, str | int | None]: The constructed management context.
        """
        return {}

    @staticmethod
    def construct_context(request: ContractRequest) -> dict[str, str | int | None] | None:
        """Construct the appropriate context based on contract type.

        This method routes the context construction to the appropriate handler
        based on the contract type specified in the request.

        Args:
            request (ContractRequest): The contract request.

        Returns
        -------
            dict[str, str | int | None] | None: The constructed context or None if
                the contract type is not supported.
        """
        if request.contract_type == ContractType.NONDISCLOSURE:
            return ContextService._construct_nondisclosure_context(request)

        if request.contract_type == ContractType.SHAREHOLDERS:
            logger.debug("Constructing shareholder's agreement context.")
            return ContextService._construct_shareholder_context(request)

        if request.contract_type == ContractType.MANAGEMENT:
            logger.debug("Constructing management agreement context.")
            return ContextService._construct_management_context(request)

        return None
