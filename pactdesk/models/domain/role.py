"""Define role models for contract document structure.

This module provides models for representing roles and responsibilities in contract
documents, including definitions for different types of roles and their associated
attributes and behaviors.
"""

from pactdesk.models.domain.enum import InformationRole, ManagementRole


Role = InformationRole | ManagementRole
