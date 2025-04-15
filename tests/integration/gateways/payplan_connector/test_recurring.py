"""
Test Recurring
"""

import datetime
import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import RecurringPaymentMethod


class IntegrationGatewaysPorticoConnectorDebitTests(unittest.TestCase):
    """
    Ensure recurring transactions work
    """

    config = PorticoConfig()
    config.secret_api_key = (
        "skapi_cert_MaePAQBr-1QAqjfckFC8FTbRTT120bVQUlfVOjgCBw"  # gitleaks:allow
    )
    config.service_url = "https://cert.api2.heartlandportico.com"

    ServicesContainer.configure(config, "recurring")

    @staticmethod
    def payment_id(payment_type):
        return "{0}-GlobalApi-{1}".format(
            datetime.date.today().isoformat(), payment_type
        )

    def test_check_crypto_gold_standard(self):
        gold_config = PorticoConfig()
        gold_config.secret_api_key = (
            "skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A"  # gitleaks:allow
        )
        gold_config.service_url = "https://cert.api2-c.heartlandportico.com"

        ServicesContainer.configure(gold_config, "gold standard")

        payment_method = RecurringPaymentMethod.find(
            self.payment_id("credit"), config_name="gold standard"
        )
        self.assertNotEqual(None, payment_method)

        response = (
            payment_method.charge(14.01)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("gold standard")
        )
        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)
