import time
import unittest
from datetime import datetime, timedelta

from globalpayments.api import ServicesContainer, GpApiConfig
from globalpayments.api.entities.enums import (
    CardChannel,
    StoredCredentialInitiator,
    StoredCredentialType,
    StoredCredentialSequence,
    StoredCredentialReason,
    Environment,
)
from globalpayments.api.entities.gp_api import AccessTokenInfo
from globalpayments.api.entities.installment_data import InstallmentData
from globalpayments.api.entities.stored_credentials import StoredCredential
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.payment_methods import CreditCardData
from globalpayments.api.services.reporting_service import ReportingService
from globalpayments.api.utils.logger import Logger


class GpApiInstallmentTests(unittest.TestCase):
    """
    Tests for installment payment plan functionality with GP API.
    """

    FIRST_PAGE = 2
    PAGE_SIZE = 10

    currency = "MXN"
    amount = 2.02

    @classmethod
    def setUpClass(cls):
        config = GpApiConfig()
        config.app_id = "4gPqnGBkppGYvoE5UX9EWQlotTxGUDbs"
        config.app_key = "FQyJA5VuEQfcji2M"
        config.channel = CardChannel.CARD_NOT_PRESENT
        config.service_url = "https://apis.sandbox.globalpay.com/ucp"
        config.environment = Environment.Test
        config.country = "MX"
        config.request_logger = Logger()

        access_token_info = AccessTokenInfo()
        access_token_info.transaction_processing_account_name = "transaction_processing"
        access_token_info.risk_assessment_account_name = "EOS_RiskAssessment"
        config.access_token_info = access_token_info

        ServicesContainer.configure(config)

        # Installment data
        cls.installment_data = InstallmentData()
        cls.installment_data.mode = "INTEREST"
        cls.installment_data.program = "SIP"
        cls.installment_data.count = "99"
        cls.installment_data.grace_period_count = "30"

        # Stored credential data
        cls.stored_credential_data = StoredCredential()
        cls.stored_credential_data.initiator = StoredCredentialInitiator.CardHolder
        cls.stored_credential_data.type = StoredCredentialType.INSTALLMENT
        cls.stored_credential_data.sequence = StoredCredentialSequence.SUBSEQUENT
        cls.stored_credential_data.reason = StoredCredentialReason.INCREMENTAL
        cls.stored_credential_data.contract_reference = "TestContractReference"

        # MasterCard
        cls.master_card = CreditCardData()
        cls.master_card.number = "5120350100064537"
        cls.master_card.exp_month = 12
        cls.master_card.exp_year = 2026
        cls.master_card.cvn = "123"
        cls.master_card.card_present = False
        cls.master_card.reader_present = False

        # Visa
        cls.visa_card = CreditCardData()
        cls.visa_card.number = "4395840190010011"
        cls.visa_card.exp_month = 4
        cls.visa_card.exp_year = 2026
        cls.visa_card.cvn = "123"
        cls.visa_card.card_present = False
        cls.visa_card.reader_present = False

        # Reporting start date
        cls.reporting_start_date = (
                datetime.now() - timedelta(days=180)
        ).strftime("%Y-%m-%d")

    def _assert_transaction_response(self, transaction, transaction_status):
        self.assertIsNotNone(transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(transaction_status, transaction.response_message)

    def test_credit_sale_for_installment_mc(self):
        response = (
            self.master_card.charge(self.amount)
            .with_currency(self.currency)
            .with_stored_credential(self.stored_credential_data)
            .with_installment_data(self.installment_data)
            .execute()
        )

        self._assert_transaction_response(response, TransactionStatus.CAPTURED)
        self.assertEqual(str(self.amount), response.balance_amount)

    def test_credit_sale_for_installment_visa(self):
        response = (
            self.visa_card.charge(self.amount)
            .with_currency(self.currency)
            .with_stored_credential(self.stored_credential_data)
            .with_installment_data(self.installment_data)
            .execute()
        )

        self._assert_transaction_response(response, TransactionStatus.CAPTURED)
        self.assertEqual(str(self.amount), response.balance_amount)

    def test_credit_sale_without_installment_data(self):
        response = (
            self.visa_card.charge(self.amount)
            .with_currency(self.currency)
            .with_stored_credential(self.stored_credential_data)
            .execute()
        )

        self._assert_transaction_response(response, TransactionStatus.CAPTURED)
        self.assertEqual(str(self.amount), response.balance_amount)
        self.assertIsNone(response.installment_data)

    def test_report_transaction_detail_for_installment_by_id(self):
        response = (
            self.master_card.charge(self.amount)
            .with_currency(self.currency)
            .with_stored_credential(self.stored_credential_data)
            .with_installment_data(self.installment_data)
            .execute()
        )

        time.sleep(3)

        transaction = ReportingService.transaction_detail(
            response.transaction_id
        ).execute()

        self.assertIsNotNone(transaction)
        self.assertIsNotNone(transaction.installment_data)
        
        self.assertEqual(
            self.installment_data.mode, transaction.installment_data.mode
        )
        self.assertEqual(
            self.installment_data.count, transaction.installment_data.count
        )
        self.assertEqual(
            self.installment_data.grace_period_count,
            transaction.installment_data.grace_period_count,
        )
        self.assertEqual(response.transaction_id, transaction.transaction_id)

    def test_report_transaction_detail_without_installment_by_id(self):
        response = (
            self.master_card.charge(self.amount)
            .with_currency(self.currency)
            .with_stored_credential(self.stored_credential_data)
            .execute()
        )

        time.sleep(3)
        transaction = ReportingService.transaction_detail(
            response.transaction_id
        ).execute()

        self.assertIsNotNone(transaction)
        self.assertEqual(response.transaction_id, transaction.transaction_id)


if __name__ == "__main__":
    unittest.main()
