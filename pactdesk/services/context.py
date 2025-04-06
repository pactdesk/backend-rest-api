from loguru import logger
from pydantic import BaseModel

from pactdesk.models.api.contract import ContractRequest
from pactdesk.models.domain.context import ContextType, PartyContextType
from pactdesk.models.domain.enum import ContractType, InformationRole, PartyType


class ContextService(BaseModel):
    @staticmethod
    def construct_party_context(request: ContractRequest) -> PartyContextType:
        total_parties = len(request.parties)
        party_context: PartyContextType = {
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
                role = party.name

            if party.party_type == PartyType.LEGAL_ENTITY.value:
                party_context[key] = {
                    "type": PartyType.LEGAL_ENTITY.value,
                    "name": party.name,
                    "company_type": party.company_type.value,
                    "country": party.country_of_incorporation,
                    "address": party.registered_address._formatted,
                    "kvk_nr": str(party.kvk_nr) if party.kvk_nr is not None else None,
                    "representative": party.signatory_name,
                    "role": role,
                }

            elif party.party_type == PartyType.NATURAL_PERSON.value:
                party_context[key] = {
                    "type": PartyType.NATURAL_PERSON.value,
                    "name": party.full_name,
                    "date_of_birth": str(party.date_of_birth)
                    if party.date_of_birth is not None
                    else None,
                    "place_of_birth": party.place_of_birth,
                    "address": party.address._formatted,
                    "role": role,
                }

        return party_context

    @staticmethod
    def _construct_nondisclosure_context(request: ContractRequest) -> ContextType:
        context: ContextType = {
            "contract_purpose": request.contract_purpose,
        }

        if request.penalty_clause:
            context["penalty_initial_amount"] = str(request.penalty_clause.initial_amount)
            context["penalty_subsequent_amount"] = str(request.penalty_clause.subsequent_amount)

        if request.limited_term:
            context["term_duration"] = str(request.limited_term.duration_amount)
            context["term_unit"] = request.limited_term.duration_unit

        return context

    @staticmethod
    def _construct_shareholder_context(request: ContractRequest) -> ContextType:
        # TODO: implement shareholder context
        return {}

    @staticmethod
    def _construct_management_context(request: ContractRequest) -> ContextType:
        # TODO: implement management context
        return {}

    @staticmethod
    def construct_context(request: ContractRequest) -> ContextType | None:
        if request.contract_type == ContractType.NONDISCLOSURE:
            return ContextService._construct_nondisclosure_context(request)
        elif request.contract_type == ContractType.SHAREHOLDERS:
            return ContextService._construct_shareholder_context(request)
        elif request.contract_type == ContractType.MANAGEMENT:
            return ContextService._construct_management_context(request)
        else:
            logger.warning(f"Unknown contract type: {request.contract_type}")
            return None
