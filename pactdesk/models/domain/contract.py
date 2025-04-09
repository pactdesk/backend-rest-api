"""
Contract domain models for the PactDesk system.

This module defines the core contract model that represents the structure of
legal contracts in the PactDesk system. It provides a standardized representation
of contracts with sections for parties, considerations, agreements, and signatures.
"""

from pydantic import BaseModel

from pactdesk.models.domain.base import Section


class Contract(BaseModel):
    """
    Model for legal contracts in the PactDesk system.

    This class represents a complete legal contract with all its essential components,
    including the parties involved, considerations exchanged, agreements made, and
    signature blocks.

    Attributes
    ----------
        parties: A section containing information about all parties involved in the contract.
        considerations: A section describing the considerations exchanged between parties.
        agreements: A section containing the main agreements and terms of the contract.
        signatures: A section with signature blocks for all parties to sign the contract.
    """

    parties: Section
    considerations: Section
    agreements: Section
    signatures: Section
