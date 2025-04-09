from loguru import logger
from pydantic import BaseModel

from pactdesk.models.api.contract import ContractRequest
from pactdesk.models.domain.enum import ContractType, InformationRole, PartyType
from pactdesk.models.domain.party import LegalEntity, NaturalPerson


class ContextService(BaseModel):
    @staticmethod
    def construct_party_context(request: ContractRequest) -> dict[str, dict[str, str | int | None]]:
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
        return {}

    @staticmethod
    def _construct_management_context(request: ContractRequest) -> dict[str, str | int | None]:
        return {}

    @staticmethod
    def construct_context(request: ContractRequest) -> dict[str, str | int | None] | None:
        if request.contract_type == ContractType.NONDISCLOSURE:
            return ContextService._construct_nondisclosure_context(request)

        if request.contract_type == ContractType.SHAREHOLDERS:
            logger.debug("Constructing shareholder's agreement context.")
            return ContextService._construct_shareholder_context(request)

        if request.contract_type == ContractType.MANAGEMENT:
            logger.debug("Constructing management agreement context.")
            return ContextService._construct_management_context(request)

        return None
