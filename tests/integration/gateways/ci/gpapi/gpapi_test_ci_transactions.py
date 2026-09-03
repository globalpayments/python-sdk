import unittest

from globalpayments.api import GpApiConfig, ServicesContainer
from globalpayments.api.entities.enums import CardChannel, Environment
from globalpayments.api.entities.gp_api import AccessTokenInfo
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.payment_methods import CreditCardData
from globalpayments.api.utils.logger import Logger
from tests.data.ci_testing_harness import CacheMode, CiTestingHarness


class GpApiTransactionsCITests(unittest.TestCase):
    APP_ID = "4gPqnGBkppGYvoE5UX9EWQlotTxGUDbs"
    APP_KEY = "FQyJA5VuEQfcji2M"
    AMOUNT = "2.02"
    CURRENCY = "USD"

    harness: CiTestingHarness

    @classmethod
    def setUpClass(cls):
        cls.harness = CiTestingHarness(
            "https://apis.sandbox.globalpay.com/ucp",
            CacheMode.Locked,
            "GpApiTransactionsCITests",
        )

    def setUp(self):
        now = self.harness.get_current_time()
        self.card = CreditCardData()
        self.card.number = "4263970000005262"
        self.card.exp_month = str(now.month).zfill(2)
        self.card.exp_year = str(now.year + 1)
        self.card.cvn = "123"
        self.card.card_present = True

    def _configure_gp_api_service(self):
        config = GpApiConfig()
        config.app_id = self.APP_ID
        config.app_key = self.APP_KEY
        config.channel = CardChannel.CARD_NOT_PRESENT
        config.environment = Environment.Test
        config.country = "US"
        config.challenge_notification_url = "https://ensi808o85za.x.pipedream.net/"
        config.method_notification_url = "https://ensi808o85za.x.pipedream.net/"
        config.merchant_contact_url = "https://enp4qhvjseljg.x.pipedream.net/"
        config.request_logger = Logger()
        access_token_info = AccessTokenInfo()
        access_token_info.transaction_processing_account_name = "transaction_processing"
        access_token_info.risk_assessment_account_name = "EOS_RiskAssessment"
        config.access_token_info = access_token_info
        config.service_url = self.harness.get_testing_url()
        ServicesContainer.configure(config)

    def _assert_transaction_response(self, transaction, status):
        self.assertIsNotNone(transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(status, transaction.response_message)

    def test_post_capture(self):
        self.harness.set_function("GP-API|Transactions|POST Capture")
        self._configure_gp_api_service()

        transaction = (
            self.card.authorize(self.AMOUNT)
            .with_currency(self.CURRENCY)
            .with_client_transaction_id(
                self.harness.generate_random_id("postCapture_auth")
            )
            .execute()
        )
        self._assert_transaction_response(transaction, TransactionStatus.PREAUTHORIZED)

        # Correction A: capture() returns a ManagementBuilder, which has no
        # with_client_transaction_id in the Python SDK.
        capture = transaction.capture(self.AMOUNT).execute()
        self._assert_transaction_response(capture, TransactionStatus.CAPTURED)

    def test_post_charge(self):
        self.harness.set_function("GP-API|Transactions|POST Create")
        self._configure_gp_api_service()

        transaction = (
            self.card.charge(self.AMOUNT)
            .with_currency(self.CURRENCY)
            .with_client_transaction_id(self.harness.generate_random_id("postCreate"))
            .execute()
        )
        self._assert_transaction_response(transaction, TransactionStatus.CAPTURED)
