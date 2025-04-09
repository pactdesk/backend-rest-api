from loguru import logger
from pydantic import BaseModel

from pactdesk.models.api.contract import ContractRequest
from pactdesk.models.domain.enum import ContractType, InformationRole, PartyType


class ContextService(BaseModel):
    # TODO: custom Pydantic schema model for dict[str, str]
    @staticmethod
    def construct_party_context(request: ContractRequest) -> dict[str, dict[str, str | None]]:
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
    def _construct_nondisclosure_context(request: ContractRequest) -> dict[str, str]:
        return {
            "city": request.place_of_jurisdiction,
            "country": request.applicable_law,
            "purpose": request.contract_purpose,
            **(
                {
                    "duration_amount": request.limited_term.duration_amount,
                    "duration_unit": request.limited_term.duration_unit,
                }
                if request.limited_term
                else {}
            ),
            **(
                {
                    "initial_amount": request.penalty_clause.initial_amount,
                    "subsequent_amount": request.penalty_clause.subsequent_amount,
                }
                if request.penalty_clause
                else {}
            ),
        }

    @staticmethod
    def _construct_shareholder_context(request: ContractRequest) -> dict[str, str]:
        return {}

    @staticmethod
    def _construct_management_context(request: ContractRequest) -> dict[str, str]:
        return {}

    @staticmethod
    def construct_context(request: ContractRequest) -> dict[str, str] | None:
        if request.contract_type == ContractType.NONDISCLOSURE:
            return ContextService._construct_nondisclosure_context(request)

        if request.contract_type == ContractType.SHAREHOLDERS:
            logger.debug("Constructing shareholder's agreement context.")
            return ContextService._construct_shareholder_context(request)

        if request.contract_type == ContractType.MANAGEMENT:
            logger.debug("Constructing management agreement context.")
            return ContextService._construct_management_context(request)

        return None
