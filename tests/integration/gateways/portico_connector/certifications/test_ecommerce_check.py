"""
Test Check
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import Address, Transaction
from globalpayments.api.entities.enums import (
    AccountType,
    CheckType,
    EntryMethod,
    PaymentMethodType,
    SecCode,
)
from globalpayments.api.payment_methods import ECheck


class IntegrationGatewaysPorticoConnectorCertificationEcommerceCheckTests(
    unittest.TestCase
):
    """
    Ensure check transactions work
    """

    config = PorticoConfig()
    config.secret_api_key = "skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A"
    config.service_url = "https://cert.api2.heartlandportico.com"
    config.developer_id = "000000"
    config.version_number = "0000"

    ServicesContainer.configure(config, "ach")

    address = Address()
    address.street_address_1 = "123 Main St."
    address.city = "Downtown"
    address.province = "NJ"
    address.postal_code = "12345"

    def check(self, sec_code, check_type, account_type, check_name=None):
        check = ECheck()
        check.account_number = "24413815"
        check.routing_number = "490000018"
        check.check_type = check_type
        check.sec_code = sec_code
        check.account_type = account_type
        check.entry_mode = EntryMethod.Manual
        check.check_holder_name = "John Doe"
        check.drivers_license_number = "09876543210"
        check.drivers_license_state = "TX"
        check.phone_number = "8003214567"
        check.birth_year = "1997"
        check.ssn_last_4 = "4321"
        if check_name:
            check.check_name = check_name
        return check

    # ACH Debit - WEB

    def test_001_web_personal_checking(self):
        check = self.check(SecCode.WEB, CheckType.Personal, AccountType.Checking)

        response = (
            check.charge(23.00)
            .with_currency("USD")
            .with_address(self.address)
            .with_allow_duplicates(True)
            .execute("ach")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_002_web_business_checking(self):
        check = self.check(SecCode.WEB, CheckType.Business, AccountType.Checking)

        response = (
            check.charge(24.00)
            .with_currency("USD")
            .with_address(self.address)
            .with_allow_duplicates(True)
            .execute("ach")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_003_web_personal_savings(self):
        check = self.check(SecCode.WEB, CheckType.Personal, AccountType.Savings)

        response = (
            check.charge(25.00)
            .with_currency("USD")
            .with_address(self.address)
            .with_allow_duplicates(True)
            .execute("ach")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_004_web_business_savings(self):
        check = self.check(SecCode.WEB, CheckType.Business, AccountType.Savings)

        response = (
            check.charge(5.00)
            .with_currency("USD")
            .with_address(self.address)
            .with_allow_duplicates(True)
            .execute("ach")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
