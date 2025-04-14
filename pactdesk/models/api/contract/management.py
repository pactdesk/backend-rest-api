"""Module for handling management contract request models.

This module provides the ManagementRequest class which represents a request to generate
a management contract. It includes validation for party roles and contract structure,
ensuring the management contract meets specific requirements such as having exactly
two parties with the roles of Principal and Contractor.
"""

from typing import Self, TypeVar

from pydantic import model_validator

from pactdesk.models.api.contract.base import BaseContractRequest
from pactdesk.models.domain.enum import ContractType, ManagementRole


T = TypeVar("T", bound="ManagementRequest")


class ManagementRequest(BaseContractRequest):
    """Model for management contract generation requests.

    This class extends BaseContractRequest to handle management-specific requirements and
    validations. It ensures proper configuration of parties and their roles in the
    management contract.

    Attributes
    ----------
        contract_type (ContractType): Always set to ContractType.MANAGEMENT for management
            contracts.
        business_activities (str): Description of the business activities to be managed.
        date_of_appointment (str): The date when the management appointment begins.
        term_start_date (str): The start date of the management term.
        notice_period_amount (str): The amount of notice required for termination.
        notice_period_unit (str): The unit of time for the notice period.
        fee_amount (str): The management fee amount.
        hours_amount (str): The number of hours to be worked.
        prior_approval_amount (str): The amount requiring prior approval.
        reimbursement_amount_of_days (str): The number of days for reimbursement.
        reimbursement_amount_unit (str): The unit of time for reimbursement.
        invoice_duration (str): The duration between invoices.
        invoice_duration_unit (str): The unit of time for invoice duration.
        applicable_law (str): The governing law for the contract.
        place_of_jurisdiction (str): The jurisdiction for legal matters.
    """

    contract_type: ContractType = ContractType.MANAGEMENT
    business_activities: str
    date_of_appointment: str
    term_start_date: str
    notice_period_amount: str
    notice_period_unit: str
    fee_amount: str
    hours_amount: str
    prior_approval_amount: str
    reimbursement_amount_of_days: str
    reimbursement_amount_unit: str
    invoice_duration: str
    invoice_duration_unit: str
    applicable_law: str
    place_of_jurisdiction: str
    
    @model_validator(mode="after")  # type: ignore[misc]
    def validate_parties(self) -> Self:
        """Validate the number of parties in the management contract.

        This validator ensures the management contract has exactly two parties.

        Returns
        -------
            Self: The validated ManagementRequest instance.

        Raises
        ------
            ValueError: If the number of parties is not exactly two.
        """
        if len(self.parties) != 2:
            err_msg = "Management contracts must have exactly two parties"
            raise ValueError(err_msg)
        
        return self

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_roles(self) -> Self:
        """Validate the management roles of parties in the contract.

        This validator ensures the management contract has exactly one Principal
        and one Contractor.

        Returns
        -------
            Self: The validated ManagementRequest instance.

        Raises
        ------
            ValueError: If the roles are not exactly one Principal and one Contractor.
        """
        roles = [party.role for party in self.parties.values()]
        if not (ManagementRole.PRINCIPAL in roles and ManagementRole.CONTRACTOR in roles):
            err_msg = "Management contracts must have exactly one Principal and one Contractor"
            raise ValueError(err_msg)
        
        return self
