import unittest
from datetime import datetime, timedelta, timezone

from globalpayments.api import ServicesContainer
from globalpayments.api.entities.enums import (
    CardChannel,
    TransactionSortProperty,
    SearchCriteria,
    PaymentMethodName,
    PaymentEntryMode,
    Channel,
    DataServiceCriteria,
    PaymentType,
)
from globalpayments.api.entities.exceptions import GatewayException
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.services import ReportingService
from globalpayments.api.utils import StringUtils
from tests.data.GpApi_test_config import GpApiTestConfig


class GpApiReportingTests(unittest.TestCase):
    """
    Integration tests for Global Payments Reporting Service
    """

    @classmethod
    def setUpClass(cls):
        # Setup configuration for reporting tests
        cls.start_date = datetime.now() - timedelta(days=30)
        cls.start_date = cls.start_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cls.end_date = datetime.now()
        cls.start_date = cls.start_date.replace(tzinfo=timezone.utc)
        cls.end_date = cls.end_date.replace(tzinfo=timezone.utc)

        # Configure services container
        config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_PRESENT)
        ServicesContainer.configure(config)

        # Class level variables to store transaction details for subsequent tests
        cls.transaction_id = None
        cls.batch_id = None
        cls.amount = None
        cls.country = None
        cls.currency = None
        cls.brand_reference = None
        cls.reference = None
        cls.card_brand = None
        cls.auth_code = None

    def test_001_find_transactions_by_date_range(self):
        """
        Find transactions within a specific date range
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            # .order_by(TransactionSortProperty.TIME_CREATED)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.EndDate, self.end_date)
            .execute()
        )

        self.assertIsNotNone(response)
        self.assertTrue(len(response.result) > 0)

        # Store details from first transaction for subsequent tests
        first_transaction = response.result[0]

        # Verify transaction date is within range
        for transaction in response.result:
            transaction_date = datetime.fromisoformat(
                transaction.transaction_date.replace("Z", "")
            )
            transaction_date.replace(tzinfo=timezone.utc)
            self.assertTrue(transaction_date >= self.start_date)
            self.assertTrue(transaction_date < self.end_date)

        # Store transaction details
        self.__class__.transaction_id = first_transaction.transaction_id
        self.__class__.batch_id = first_transaction.batch_sequence_number
        self.__class__.amount = first_transaction.amount
        self.__class__.country = first_transaction.country
        self.__class__.currency = first_transaction.currency
        self.__class__.brand_reference = first_transaction.brand_reference
        self.__class__.reference = first_transaction.reference_number
        self.__class__.card_brand = first_transaction.card_type
        self.__class__.auth_code = first_transaction.auth_code

    def test_002_find_transactions_by_transaction_id(self):
        """
        Find transactions by a specific transaction ID
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .with_transaction_id(self.transaction_id)
            .where(SearchCriteria.StartDate, self.start_date)
            .execute()
        )

        self.assertEqual(len(response.result), 1)
        self.assertEqual(self.transaction_id, response.result[0].transaction_id)

    def test_003_find_transactions_with_wrong_transaction_id(self):
        """
        Attempt to find transactions with an incorrect transaction ID
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .with_transaction_id("TRN_B2RDfsrhwhzvsbkci4JdTiZ9mHVmvC")
            .where(SearchCriteria.StartDate, self.start_date)
            .execute()
        )

        self.assertEqual(len(response.result), 0)

    def test_004_find_transactions_by_batch_id(self):
        """
        Find transactions by batch ID
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.BatchId, self.batch_id)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        for transaction in response.result:
            self.assertEqual(self.batch_id, transaction.batch_sequence_number)

    def test_005_find_transactions_by_payment_type(self):
        """
        Find transactions by payment type
        """
        payment_type = PaymentType.SALE
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.PaymentType, payment_type)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        for transaction in response.result:
            self.assertEqual(payment_type.value, transaction.transaction_type)

    def test_006_find_transactions_by_amount_currency_country(self):
        """
        Find transactions by amount, currency, and country
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(DataServiceCriteria.Amount, self.amount)
            .and_with(DataServiceCriteria.Currency, self.currency)
            .and_with(DataServiceCriteria.Country, self.country)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        for transaction in response.result:
            self.assertEqual(self.amount, transaction.amount)
            self.assertEqual(self.currency, transaction.currency)
            self.assertEqual(self.country, transaction.country)

    def test_007_find_transactions_by_channel(self):
        """
        Find transactions by channel
        """
        channel = Channel.CardNotPresent
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.Channel, channel)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        for transaction in response.result:
            self.assertEqual(channel.value, transaction.channel)

    def test_008_find_transactions_by_status(self):
        """
        Find transactions by status
        """
        status = TransactionStatus.CAPTURED
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.TransactionStatus, status)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertEqual(status, response.result[0].transaction_status)

    def test_009_find_transactions_by_card_brand_and_auth_code(self):
        """
        Find transactions by card brand and authorization code
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.CardBrand, self.card_brand)
            .and_with(SearchCriteria.AuthCode, self.auth_code)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertEqual(self.card_brand, response.result[0].card_type)
        self.assertEqual(self.auth_code, response.result[0].auth_code)

    def test_010_find_transactions_by_reference(self):
        """
        Find transactions by reference number
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.ReferenceNumber, self.reference)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertEqual(self.reference, response.result[0].reference_number)

    def test_011_find_transactions_by_brand_reference(self):
        """
        Find transactions by brand reference
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.BrandReference, self.brand_reference)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        for transaction in response.result:
            self.assertEqual(self.brand_reference, transaction.brand_reference)

    def test_012_find_transactions_by_entry_mode(self):
        """
        Find transactions by payment entry mode
        """
        payment_entry_mode = PaymentEntryMode.ECOM
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.PaymentEntryMode, payment_entry_mode)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertEqual(payment_entry_mode, response.result[0].entry_mode)

    def test_013_find_transactions_by_card_number(self):
        """
        Find transactions by first 6 and last 4 digits of card number
        """
        first_six = "426397"
        last_four = "5262"
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.CardNumberFirstSix, first_six)
            .and_with(SearchCriteria.CardNumberLastFour, last_four)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertTrue(
            response.result[0].masked_card_number.startswith(first_six)
            and response.result[0].masked_card_number.endswith(last_four)
        )

    def test_014_find_transactions_by_token_and_payment_method(self):
        """
        Attempt to find transactions by token with an incorrect payment method
        """
        first_six = "426397"
        last_four = "5262"

        with self.assertRaises(GatewayException) as context:
            (
                ReportingService.find_transactions_paged(1, 10)
                .where(SearchCriteria.StartDate, self.start_date)
                .and_with(SearchCriteria.TokenFirstSix, first_six)
                .and_with(SearchCriteria.TokenLastFour, last_four)
                .and_with(SearchCriteria.PaymentMethodName, PaymentMethodName.CARD)
                .execute()
            )

        error = context.exception
        self.assertEqual(error.response_code, "40043")
        self.assertIn(
            "Status Code: INVALID_REQUEST_DATA - Request contains unexpected fields: payment_method",
            error.message,
        )

    def test_015_find_transactions_by_payment_method_name(self):
        """
        Find transactions by payment method name
        """
        payment_method_name = PaymentMethodName.DIGITAL_WALLET
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.PaymentMethodName, payment_method_name)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertEqual(payment_method_name, response.result[0].payment_type)

    def test_016_find_transactions_by_name(self):
        """
        Find transactions by cardholder name
        """
        cardholder_name = "James Mason"
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .where(SearchCriteria.StartDate, self.start_date)
            .and_with(SearchCriteria.Name, cardholder_name)
            .execute()
        )

        self.assertTrue(len(response.result) >= 1)
        self.assertEqual(cardholder_name, response.result[0].card_holder_name)

    @unittest.skip("Skipping this test - order criteria difference")
    def test_017_find_transactions_order_by_id(self):
        """
        Find transactions ordered by transaction ID
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .order_by(TransactionSortProperty.ID)
            .where(SearchCriteria.StartDate, self.start_date)
            .execute()
        )

        self.assertTrue(len(response.result) > 1)
        transactions = sorted(response.result, key=lambda x: x.transaction_id)

        for i, transaction in enumerate(response.result):
            self.assertEqual(transaction.transaction_id, transactions[i].transaction_id)

    def test_018_find_transactions_order_by_type(self):
        """
        Find transactions ordered by transaction type
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .order_by(TransactionSortProperty.TYPE)
            .where(SearchCriteria.StartDate, self.start_date)
            .execute()
        )

        self.assertTrue(len(response.result) > 1)
        transactions = sorted(response.result, key=lambda x: x.transaction_type)

        for i, transaction in enumerate(response.result):
            self.assertEqual(
                transaction.transaction_type, transactions[i].transaction_type
            )

    @unittest.skip("Skipping this test - order criteria difference")
    def test_019_find_transactions_order_by_time_created(self):
        """
        Find transactions ordered by time created
        """
        response = (
            ReportingService.find_transactions_paged(1, 10)
            .order_by(TransactionSortProperty.TIME_CREATED)
            .where(SearchCriteria.StartDate, self.start_date)
            .execute()
        )

        self.assertTrue(len(response.result) > 1)
        transactions = sorted(
            response.result,
            key=lambda x: datetime.fromisoformat(x.transaction_date.replace("Z", "")),
        )

        for i, transaction in enumerate(response.result):
            transaction_date = datetime.fromisoformat(
                transaction.transaction_date.replace("Z", "")
            )
            sorted_transaction_date = datetime.fromisoformat(
                transactions[i].transaction_date.replace("Z", "")
            )
            self.assertEqual(transaction_date, sorted_transaction_date)

    def test_020_find_transactions_without_mandatory_start_date(self):
        """
        Find transactions without specifying a mandatory start date
        """
        tonight = datetime.now() + timedelta(days=1)
        tonight = tonight.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )

        response = ReportingService.find_transactions_paged(1, 10).execute()

        self.assertTrue(len(response.result) >= 0)

        for transaction in response.result:
            transaction_date = datetime.fromisoformat(
                transaction.transaction_date.replace("Z", "")
            ).replace(tzinfo=timezone.utc)
            self.assertTrue(transaction_date < tonight)

    def test_021_transaction_details_report(self):
        """
        Retrieve transaction details for a specific transaction ID
        """
        transaction_id = "TRN_RyWZELCUbOq12IPDowbOevTC9BZxZi_6827116a3d1b"
        response = ReportingService.transaction_detail(transaction_id).execute()

        self.assertIsNotNone(response)
        self.assertEqual(response.transaction_id, transaction_id)

    def test_022_transaction_details_report_wrong_id(self):
        """
        Attempt to retrieve transaction details with an incorrect transaction ID
        """
        transaction_id = str(StringUtils.uuid())

        with self.assertRaises(GatewayException) as context:
            ReportingService.transaction_detail(transaction_id).execute()

        error = context.exception
        self.assertEqual(error.response_code, "40118")
        self.assertIn(
            f"Status Code: RESOURCE_NOT_FOUND - Transactions {transaction_id} not found at this /ucp/transactions/{transaction_id}",
            error.message,
        )

    @classmethod
    def tearDownClass(cls):
        """
        Reset the GP API configuration after all tests
        """
        GpApiTestConfig.reset_gpapi_config()
