"""
Context service for the PactDesk system.

This module provides services for constructing context dictionaries that are used
to render contract templates. It extracts relevant information from contract requests
and formats it into a structure that can be used by template engines.
"""

from loguru import logger
from pydantic import BaseModel

from pactdesk.models.api.contract import ContractRequest
from pactdesk.models.domain.enum import ContractType, InformationRole, PartyType


class ContextService(BaseModel):
    """
    Service for constructing context dictionaries for contract templates.

    This class provides methods for extracting and formatting information from
    contract requests into context dictionaries that can be used to render
    contract templates. It handles different contract types and party types,
    ensuring that all necessary information is included in the context.

    Attributes
    ----------
        None: This class does not have any attributes as it only provides
            static methods for context construction.
    """

    # TODO: custom Pydantic schema model for dict[str, str]
    @staticmethod
    def construct_party_context(request: ContractRequest) -> dict[str, dict[str, str | int | None]]:
        """
        Construct a context dictionary for party information.

        This method extracts party information from a contract request and formats
        it into a context dictionary that can be used to render party-specific
        sections of contract templates. It handles both legal entities and natural
        persons, and assigns appropriate roles based on the number of parties.

        Parameters
        ----------
            request: The contract request containing party information.

        Returns
        -------
            A dictionary mapping party keys to dictionaries of party information.

        Raises
        ------
            ValueError: If a party has an invalid party type.
        """
        total_parties = len(request.parties)
        party_context = {
            "_global": {
                "n_parties": total_parties,
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
                role = party.name

            if party.party_type == PartyType.LEGAL_ENTITY.value:
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

            elif party.party_type == PartyType.NATURAL_PERSON.value:
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
    def _construct_nondisclosure_context(request: ContractRequest) -> dict[str, str | int]:
        """
        Construct a context dictionary for nondisclosure agreement information.

        This method extracts nondisclosure-specific information from a contract
        request and formats it into a context dictionary that can be used to
        render nondisclosure agreement templates.

        Parameters
        ----------
            request: The contract request containing nondisclosure information.

        Returns
        -------
            A dictionary of nondisclosure agreement context information.
        """
        result: dict[str, str | int] = {
            "city": request.place_of_jurisdiction,
            "country": request.applicable_law,
            "purpose": request.contract_purpose,
        }

        if request.limited_term:
            result["duration_amount"] = request.limited_term.duration_amount
            result["duration_unit"] = request.limited_term.duration_unit

        if request.penalty_clause:
            result["initial_amount"] = request.penalty_clause.initial_amount
            result["subsequent_amount"] = request.penalty_clause.subsequent_amount

        return result

    @staticmethod
    def _construct_shareholder_context(request: ContractRequest) -> dict[str, str]:
        """
        Construct a context dictionary for shareholders agreement information.

        This method extracts shareholders agreement-specific information from a
        contract request and formats it into a context dictionary that can be
        used to render shareholders agreement templates.

        Parameters
        ----------
            request: The contract request containing shareholders agreement information.

        Returns
        -------
            A dictionary of shareholders agreement context information.
        """
        return {}

    @staticmethod
    def _construct_management_context(request: ContractRequest) -> dict[str, str]:
        """
        Construct a context dictionary for management agreement information.

        This method extracts management agreement-specific information from a
        contract request and formats it into a context dictionary that can be
        used to render management agreement templates.

        Parameters
        ----------
            request: The contract request containing management agreement information.

        Returns
        -------
            A dictionary of management agreement context information.
        """
        return {}

    @staticmethod
    def construct_context(request: ContractRequest) -> dict[str, str | int] | None:
        """
        Construct a context dictionary based on the contract type.

        This method determines the contract type and calls the appropriate
        context construction method to generate a context dictionary for
        rendering the contract template.

        Parameters
        ----------
            request: The contract request containing all contract information.

        Returns
        -------
            A dictionary of context information for the specific contract type,
            or None if the contract type is not supported.
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
