import unittest

from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.payment_methods import CreditCardData
from tests.data.ci_testing_harness import CacheMode, CiTestingHarness


class PorticoCreditCITests(unittest.TestCase):
    harness: CiTestingHarness

    @classmethod
    def setUpClass(cls):
        cls.harness = CiTestingHarness(
            "https://cert.api2.heartlandportico.com",
            CacheMode.Locked,
            "PorticoCreditCITests",
        )

    def setUp(self):
        self.card = CreditCardData()
        self.card.number = "4111111111111111"
        self.card.exp_month = "12"
        self.card.exp_year = "2025"
        self.card.cvn = "123"

    def _configure_portico_service(self):
        config = PorticoConfig()
        config.secret_api_key = "skapi_cert_MTeSAQAfG1UA9qQDrzl-kz4toXvARyieptFwSKP24w"
        config.developer_id = "002914"
        config.version_number = "3026"
        config.service_url = self.harness.get_testing_url()
        ServicesContainer.configure(config)

    def test_credit_sale(self):
        self.harness.set_function("Portico|Credit Transactions|CreditSale")
        self._configure_portico_service()
        client_txn_id = self.harness.generate_random_id("creditSale")

        # Correction F: the Python SDK has no with_unique_device_id builder method.
        response = (
            self.card.charge(15.5)
            .with_currency("USD")
            .with_client_transaction_id(client_txn_id)
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertIsNotNone(response)
        self.assertEqual("00", response.response_code)
        # Correction G: Python's Portico connector does not map ClientTxnId onto the
        # transaction response (Java does at PorticoConnector.java:973; Python maps it only
        # for reporting summaries). The request still sends client_txn_id; the echo assert is dropped.

    def test_credit_txn_edit(self):
        self.harness.set_function(
            "Portico|Credit Transactions|CreditTxnEdit - aka Gratuity"
        )
        self._configure_portico_service()
        client_txn_id = self.harness.generate_random_id("creditTxnEdit_charge")

        charge = (
            self.card.charge(15)
            .with_currency("USD")
            .with_client_transaction_id(client_txn_id)
            .with_allow_duplicates(True)
            .execute()
        )
        self.assertIsNotNone(charge)
        self.assertEqual("00", charge.response_code)

        # Corrections A + D: edit() is param-less and the ManagementBuilder has
        # no with_client_transaction_id in the Python SDK.
        edit = (
            charge.edit()
            .with_amount(17)
            .with_currency("USD")
            .with_gratuity(2)
            .execute()
        )
        self.assertIsNotNone(edit)
        self.assertEqual("00", edit.response_code)
