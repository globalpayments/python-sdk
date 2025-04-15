"""
Test CreditAuth
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.payment_methods import CreditCardData


class CreditAuthTests(unittest.TestCase):
    """
    Ensure CreditAuth transaction works
    """

    config = PorticoConfig()
    config.secret_api_key = (
        "skapi_cert_MTeSAQAfG1UA9qQDrzl-kz4toXvARyieptFwSKP24w"  # gitleaks:allow
    )
    config.service_url = "https://cert.api2.heartlandportico.com"

    ServicesContainer.configure(config)

    card = CreditCardData()
    card.number = "4111111111111111"
    card.exp_month = "12"
    card.exp_year = "2025"
    card.cvn = "123"
    card.card_holder_name = "Joe Smith"

    def test_credit_auth(self):
        response = (
            self.card.authorize(10)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)
