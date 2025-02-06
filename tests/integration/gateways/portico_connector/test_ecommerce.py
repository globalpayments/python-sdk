"""
Test ecommerce
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import ECommerceInfo, EncryptionData, Transaction
from globalpayments.api.entities.enums import ECommerceChannel
from globalpayments.api.entities.exceptions import UnsupportedTransactionException
from globalpayments.api.payment_methods import CreditCardData


class IntegrationGatewaysPorticoConnectorEbtTests(unittest.TestCase):
    """
    Ensure ecommerce transactions work
    """

    config = PorticoConfig()
    config.secret_api_key = "skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A"
    config.service_url = "https://cert.api2.heartlandportico.com"
    config.developer_id = "000000"
    config.version_number = "0000"

    ServicesContainer.configure(config, "ecommerce")

    card = CreditCardData()
    card.number = "4012002000060016"
    card.exp_month = "12"
    card.exp_year = "2025"
    card.cvn = "123"

    def test_ecom_with_moto(self):
        ecom = ECommerceInfo()
        ecom.channel = ECommerceChannel.MOTO

        response = (
            self.card.charge(9)
            .with_currency("USD")
            .with_ecommerce_info(ecom)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_ecom_with_direct_market_ship_date(self):
        ecom = ECommerceInfo()
        ecom.channel = ECommerceChannel.ECOM
        ecom.ship_day = "25"
        ecom.ship_month = "12"

        response = (
            self.card.charge(9)
            .with_currency("USD")
            .with_ecommerce_info(ecom)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_ecom_with_direct_market_invoice_no_ship_date(self):
        response = (
            self.card.charge(9)
            .with_currency("USD")
            .with_ecommerce_info(ECommerceInfo())
            .with_invoice_number("1234567890")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_ecom_with_direct_market_invoice_and_ship_date(self):
        ecom = ECommerceInfo()
        ecom.channel = ECommerceChannel.ECOM
        ecom.ship_month = "25"
        ecom.ship_month = "12"

        response = (
            self.card.charge(9)
            .with_currency("USD")
            .with_ecommerce_info(ecom)
            .with_invoice_number("1234567890")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_ecom_with_secure_ecommerce(self):
        ecom = ECommerceInfo()
        ecom.channel = ECommerceChannel.ECOM
        ecom.payment_data_source = "ApplePay"
        ecom.cavv = "XXXXf98AAajXbDRg3HSUMAACAAA="
        ecom.eci = "5"

        response = (
            self.card.charge(9)
            .with_currency("USD")
            .with_ecommerce_info(ecom)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)
