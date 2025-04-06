from enum import Enum


class ContractType(str, Enum):
    NONDISCLOSURE = "nondisclosure"
    SHAREHOLDERS = "shareholders"
    MANAGEMENT = "management"
    LOAN = "loan"
    OPTION = "option"


class NdaContractVariant(str, Enum):
    UNILATERAL_STANDARD = "unilateral/standard"
    UNILATERAL_MULTI = "unilateral/multi"
    MUTUAL_STANDARD = "mutual/standard"
    MUTUAL_MULTI = "mutual/multi"


class PartyType(str, Enum):
    NATURAL_PERSON = "natural_person"
    LEGAL_ENTITY = "legal_entity"


class InformationRole(str, Enum):
    DISCLOSING = "DISCLOSING"
    RECEIVING = "RECEIVING"
    MUTUAL = "MUTUAL"


class CompanyType(str, Enum):
    LLC = "LLC"
    FOUNDATION = "Foundation"
    BV = "B.V."
    NV = "N.V."
