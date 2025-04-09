"""
Enumeration types for the PactDesk system.

This module defines various enumeration types used throughout the PactDesk system
to represent contract types, party types, information roles, and company types.
These enums provide type safety and standardized values for the system's domain models.
"""

from enum import Enum


class ContractType(str, Enum):
    """
    Enumeration of contract types supported by the PactDesk system.

    This enum defines the different types of contracts that can be generated
    by the system, each with its own specific template and validation rules.

    Values
    ------
        NONDISCLOSURE: Nondisclosure agreement (NDA)
        SHAREHOLDERS: Shareholders agreement
        MANAGEMENT: Management agreement
        LOAN: Loan agreement
        OPTION: Option agreement
    """

    NONDISCLOSURE = "nondisclosure"
    SHAREHOLDERS = "shareholders"
    MANAGEMENT = "management"
    LOAN = "loan"
    OPTION = "option"


class NdaContractVariant(str, Enum):
    """
    Enumeration of NDA contract variants supported by the PactDesk system.

    This enum defines the different variants of nondisclosure agreements that
    can be generated, based on the number of parties and the standard of
    confidentiality required.

    Values
    ------
        UNILATERAL_STANDARD: One-way NDA with standard confidentiality terms
        UNILATERAL_MULTI: One-way NDA with multi-party support
        MUTUAL_STANDARD: Two-way NDA with standard confidentiality terms
        MUTUAL_MULTI: Two-way NDA with multi-party support
    """

    UNILATERAL_STANDARD = "unilateral/standard"
    UNILATERAL_MULTI = "unilateral/multi"
    MUTUAL_STANDARD = "mutual/standard"
    MUTUAL_MULTI = "mutual/multi"


class PartyType(str, Enum):
    """
    Enumeration of party types supported by the PactDesk system.

    This enum defines the different types of parties that can be involved in
    a contract, each with its own specific attributes and validation rules.

    Values
    ------
        NATURAL_PERSON: An individual person
        LEGAL_ENTITY: A company, organization, or other legal entity
    """

    NATURAL_PERSON = "natural_person"
    LEGAL_ENTITY = "legal_entity"


class InformationRole(str, Enum):
    """
    Enumeration of information roles in nondisclosure agreements.

    This enum defines the different roles that parties can have regarding
    confidential information in an NDA, determining their rights and obligations.

    Values
    ------
        DISCLOSING: The party disclosing confidential information
        RECEIVING: The party receiving confidential information
        MUTUAL: Both parties are disclosing and receiving information
    """

    DISCLOSING = "DISCLOSING"
    RECEIVING = "RECEIVING"
    MUTUAL = "MUTUAL"


class CompanyType(str, Enum):
    """
    Enumeration of company types supported by the PactDesk system.

    This enum defines the different types of legal entities that can be
    parties to a contract, each with its own specific attributes and
    validation rules.

    Values
    ------
        LLC: Limited Liability Company
        FOUNDATION: Foundation (Stichting)
        BV: Besloten Vennootschap (Private Limited Company)
        NV: Naamloze Vennootschap (Public Limited Company)
    """

    LLC = "LLC"
    FOUNDATION = "Foundation"
    BV = "B.V."
    NV = "N.V."
