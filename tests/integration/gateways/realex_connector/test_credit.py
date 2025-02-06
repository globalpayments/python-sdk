"""
Test Credit
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import Address
from globalpayments.api.entities.enums import (
    AddressType,
    RecurringSequence,
    RecurringType,
)
from globalpayments.api.payment_methods import CreditCardData


class IntegrationGatewaysRealexConnectorCreditTests(unittest.TestCase):
    """
    Ensure Credit transactions works
    """

    config = PorticoConfig()
    config.merchant_id = "heartlandgpsandbox"
    config.account_id = "api"
    config.shared_secret = "secret"
    config.rebate_password = "rebate"
    config.refund_password = "refund"
    config.service_url = "https://api.sandbox.realexpayments.com/epage-remote.cgi"

    ServicesContainer.configure(config, "realex")

    card = CreditCardData()
    card.number = "4111111111111111"
    card.exp_month = "12"
    card.exp_year = "2025"
    card.cvn = "123"
    card.card_holder_name = "Joe Smith"

    def test_credit_authorization(self):
        response = (
            self.card.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        capture = response.capture(14).execute("realex")

        self.assertNotEqual(None, capture)
        self.assertEqual("00", capture.response_code)

    def test_credit_sale(self):
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_sale_with_recurring(self):
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_recurring_info(RecurringType.Fixed, RecurringSequence.First)
            .with_allow_duplicates(True)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_refund(self):
        response = (
            self.card.refund(16)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_rebate(self):
        response = (
            self.card.charge(17)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        rebate = response.refund(17).with_currency("USD").execute("realex")

        self.assertNotEqual(None, rebate)
        self.assertEqual("00", rebate.response_code)

    def test_credit_void(self):
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        void_response = response.void().execute("realex")

        self.assertNotEqual(None, void_response)
        self.assertEqual("00", void_response.response_code)

    def test_credit_verify(self):
        response = self.card.verify().with_allow_duplicates(True).execute("realex")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_fraud_response(self):
        billing_address = Address()
        billing_address.street_address_1 = "Flat 123"
        billing_address.street_address_2 = "House 456"
        billing_address.street_address_3 = "Cul-De-Sac"
        billing_address.city = "Halifax"
        billing_address.province = "West Yorkshire"
        billing_address.state = "Yorkshire and the Humber"
        billing_address.country = "GB"
        billing_address.postal_code = "E77 4QJ"

        shipping_address = Address()
        shipping_address.street_address_1 = "House 456"
        shipping_address.street_address_2 = "987 The Street"
        shipping_address.street_address_3 = "Basement Flat"
        shipping_address.city = "Chicago"
        shipping_address.state = "Illinois"
        shipping_address.province = "Mid West"
        shipping_address.country = "US"
        shipping_address.postal_code = "5001"

        response = (
            self.card.charge(199.99)
            .with_currency("EUR")
            .with_address(billing_address, AddressType.Billing)
            .with_address(shipping_address, AddressType.Shipping)
            .with_product_id("SID9838383")
            .with_client_transaction_id("Car Part HV")
            .with_customer_id("E8953893489")
            .with_customer_ip_address("123.123.123.123")
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)
