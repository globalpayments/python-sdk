"""
Builder for creating search criteria for transaction reports
"""

from datetime import datetime
from typing import Optional, List, Any

from ...entities.address import Address
from ...entities.enums import (
    EcommerceChannel,
    DisputeStage,
    DisputeStatus,
    FraudFilterMode,
    PayByLinkStatus,
    PaymentMethodName,
    PaymentMethodType,
    PaymentMethodUsageMode,
    PaymentProvider,
    ReasonCode,
    TransactionType,
    SearchCriteria,
)
from ...entities.exceptions import ArgumentException
from ...payment_methods.payment_interfaces import PaymentMethod


class SearchCriteriaBuilder:
    """
    Builder for constructing search criteria for transaction reports
    """

    def __init__(self, report_builder):
        """
        Initialize a new SearchCriteriaBuilder

        Args:
            report_builder: The transaction report builder to use
        """
        self.report_builder = report_builder

        # Use camelCase names exactly matching the SearchCriteria enum values
        self.accountId: Optional[str] = None
        self.accountName: Optional[str] = None
        self.accountNumberLastFour: Optional[str] = None
        self.altPaymentStatus: Optional[str] = None
        self.amount: Optional[float] = None
        self.aquirerReferenceNumber: Optional[str] = None
        self.authCode: Optional[str] = None
        self.bankAccountNumber: Optional[str] = None
        self.bankRoutingNumber: Optional[str] = None
        self.batchId: Optional[str] = None
        self.batchSequenceNumber: Optional[str] = None
        self.brandReference: Optional[str] = None
        self.buyerEmailAddress: Optional[str] = None
        self.cardBrand: Optional[str] = None
        self.cardHolderFirstName: Optional[str] = None
        self.cardHolderLastName: Optional[str] = None
        self.cardHolderPoNumber: Optional[str] = None
        self.cardNumberFirstSix: Optional[str] = None
        self.cardNumberLastFour: Optional[str] = None
        self.cardTypes: Optional[List[str]] = None
        self.channel: Optional[EcommerceChannel] = None
        self.checkFirstName: Optional[str] = None
        self.checkLastName: Optional[str] = None
        self.checkName: Optional[str] = None
        self.checkNumber: Optional[str] = None
        self.clerkId: Optional[str] = None
        self.clientTransactionId: Optional[str] = None
        self.country: Optional[str] = None
        self.currency: Optional[str] = None
        self.customerId: Optional[str] = None
        self.depositId: Optional[str] = None
        self.depositReference: Optional[str] = None
        self.depositStatus: Optional[str] = None
        self.displayName: Optional[str] = None
        self.disputeId: Optional[str] = None
        self.disputeDocumentId: Optional[str] = None
        self.disputeStage: Optional[DisputeStage] = None
        self.disputeStatus: Optional[DisputeStatus] = None
        self.endBatchDate: Optional[datetime] = None
        self.endDate: Optional[datetime] = None
        self.fromTimeLastUpdated: Optional[str] = None
        self.toTimeLastUpdated: Optional[str] = None
        self.endDepositDate: Optional[datetime] = None
        self.endStageDate: Optional[datetime] = None
        self.fullyCaptured: Optional[bool] = None
        self.giftCurrency: Optional[str] = None
        self.giftMaskedAlias: Optional[str] = None
        self.hierarchy: Optional[str] = None
        self.invoiceNumber: Optional[str] = None
        self.issuerResult: Optional[str] = None
        self.issuerTransactionId: Optional[str] = None
        self.localTransactionEndTime: Optional[datetime] = None
        self.localTransactionStartTime: Optional[datetime] = None
        self.merchantId: Optional[str] = None
        self.name: Optional[str] = None
        self.oneTime: Optional[bool] = None
        self.orderId: Optional[str] = None
        self.paymentEntryMode: Optional[str] = None
        self.paymentType: Optional[str] = None
        self.paymentMethodName: Optional[PaymentMethodName] = None
        self.paymentProvider: Optional[PaymentProvider] = None
        self.paymentMethod: Optional[PaymentMethod] = None
        self.paymentMethodUsageMode: Optional[PaymentMethodUsageMode] = None
        self.paymentMethodKey: Optional[str] = None
        self.paymentMethodType: Optional[PaymentMethodType] = None
        self.referenceNumber: Optional[str] = None
        self.transactionType: Optional[List[TransactionType]] = None
        self.settlementAmount: Optional[float] = None
        self.settlementDisputeId: Optional[str] = None
        self.storedPaymentMethodId: Optional[str] = None
        self.storedPaymentMethodStatus: Optional[str] = None
        self.scheduleId: Optional[str] = None
        self.siteTrace: Optional[str] = None
        self.startBatchDate: Optional[datetime] = None
        self.startDate: Optional[datetime] = None
        self.startDepositDate: Optional[datetime] = None
        self.startStageDate: Optional[datetime] = None
        self.systemHierarchy: Optional[str] = None
        self.tokenFirstSix: Optional[str] = None
        self.tokenLastFour: Optional[str] = None
        self.transactionStatus: Optional[str] = None
        self.uniqueDeviceId: Optional[str] = None
        self.username: Optional[str] = None
        self.timezone: Optional[str] = None
        self.actionId: Optional[str] = None
        self.actionType: Optional[str] = None
        self.resource: Optional[str] = None
        self.resourceStatus: Optional[str] = None
        self.resourceId: Optional[str] = None
        self.merchantName: Optional[str] = None
        self.appName: Optional[str] = None
        self.version: Optional[str] = None
        self.responseCode: Optional[str] = None
        self.httpResponseCode: Optional[str] = None
        self.payByLinkId: Optional[str] = None
        self.description: Optional[str] = None
        self.expirationDate: Optional[datetime] = None
        self.payByLinkStatus: Optional[PayByLinkStatus] = None
        self.address: Optional[Address] = None
        self.bankPaymentId: Optional[str] = None
        self.returnPii: Optional[bool] = None
        self.riskAssessmentMode: Optional[FraudFilterMode] = None
        self.riskAssessmentReasonCode: Optional[ReasonCode] = None

    def and_with(
        self, criteria_enum: SearchCriteria, value: Any
    ) -> "SearchCriteriaBuilder":
        """
        Set a search criteria attribute with the given value

        Args:
            criteria_enum: The name of the criteria attribute to set
            value: The value to set for the criteria

        Returns:
            Self for method chaining
        """
        setattr(self, criteria_enum.value, value)
        return self

    def execute(self, config_name: str = "default") -> Any:
        """
        Execute the search using the configured criteria

        Args:
            config_name: The configuration to use for the search

        Returns:
            The search results

        Raises:
            ArgumentError: If the report builder is not set
        """
        if not self.report_builder:
            raise ArgumentException(
                f"ReportBuilder is null in {self.__class__.__name__}"
            )
        return self.report_builder.execute(config_name)
