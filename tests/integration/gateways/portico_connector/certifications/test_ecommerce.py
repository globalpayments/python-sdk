"""
Test ecommerce
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import Address
from globalpayments.api.entities.enums import TaxType, TransactionModifier
from globalpayments.api.payment_methods import CreditCardData, CreditTrackData, GiftCard
from globalpayments.api.services import BatchService
from tests.data import TestCards

use_prepaid = False

visa_token = None
mastercard_token = None
discover_token = None
amex_token = None


class IntegrationGatewaysPorticoConnectorCertificationEcommerceTests(unittest.TestCase):
    """
    Ensure ecommerce transactions work
    """

    BATCH_NOT_OPEN = "Transaction was rejected because it requires a batch to be open."
    BATCH_EMPTY = "Batch close was rejected because no transactions are associated with the currently open batch"

    config = PorticoConfig()
    config.secret_api_key = (
        "skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A"  # gitleaks:allow
    )
    config.service_url = "https://cert.api2.heartlandportico.com"
    config.developer_id = "000000"
    config.version_number = "0000"

    ServicesContainer.configure(config, "ecommerce")

    use_tokens = True

    def test_000_close_batch(self):
        try:
            response = BatchService.close_batch("ecommerce")
            self.assertNotEqual(None, response)
        except Exception as e:
            if (
                str(e.message).find(self.BATCH_NOT_OPEN) != -1
                or str(e.message).find(self.BATCH_EMPTY) != -1
            ):
                return

    # Account verification

    def test_001_verify_visa(self):
        card = TestCards.visa_manual()

        response = (
            card.verify()
            .with_request_multi_use_token(self.use_tokens)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_002_verify_mastercard(self):
        card = TestCards.mastercard_manual()

        response = (
            card.verify()
            .with_request_multi_use_token(self.use_tokens)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_003_verify_discover(self):
        card = TestCards.discover_manual()

        address = Address()
        address.postal_code = "75024"

        response = (
            card.verify()
            .with_address(address)
            .with_request_multi_use_token(self.use_tokens)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    # Address verificaiton

    def test_004_verify_amex(self):
        card = TestCards.amex_manual()

        address = Address()
        address.postal_code = "75024"

        response = (
            card.verify()
            .with_address(address)
            .with_request_multi_use_token(self.use_tokens)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    # Balance Inquiry (prepaid)

    def test_005_balance_inquiry_visa(self):
        card = TestCards.visa_swipe()

        response = card.balance_inquiry().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    # Credit Sale (with token request)

    def test_006_charge_visa_token(self):
        global visa_token

        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        response = (
            card.charge(13.01)
            .with_currency("USD")
            .with_address(address)
            .with_request_multi_use_token(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertNotEqual(None, response.token)

        visa_token = response.token

    def test_007_charge_mastercard_token(self):
        global mastercard_token

        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(13.02)
            .with_currency("USD")
            .with_address(address)
            .with_request_multi_use_token(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertNotEqual(None, response.token)

        mastercard_token = response.token

    def test_008_charge_discover_token(self):
        global discover_token

        card = TestCards.discover_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        response = (
            card.charge(13.03)
            .with_currency("USD")
            .with_address(address)
            .with_request_multi_use_token(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertNotEqual(None, response.token)

        discover_token = response.token

    def test_009_charge_amex_token(self):
        global amex_token

        card = TestCards.amex_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        response = (
            card.charge(13.04)
            .with_currency("USD")
            .with_address(address)
            .with_request_multi_use_token(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertNotEqual(None, response.token)

        amex_token = response.token

    # Credit Sale

    def test_010_charge_visa(self):
        global visa_token

        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        if self.use_tokens:
            card = CreditCardData()
            card.token = visa_token

        response = (
            card.charge(17.01)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        void_response = response.void().execute("ecommerce")

        self.assertNotEqual(None, void_response)
        self.assertEqual(
            "00", void_response.response_code, void_response.response_message
        )

    def test_011_charge_mastercard(self):
        global mastercard_token

        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        if self.use_tokens:
            card = CreditCardData()
            card.token = mastercard_token

        response = (
            card.charge(17.02)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_012_charge_discover(self):
        global discover_token

        card = TestCards.discover_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "750241234"

        if self.use_tokens:
            card = CreditCardData()
            card.token = discover_token

        response = (
            card.charge(17.03)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_013_charge_amex(self):
        global amex_token

        card = TestCards.amex_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        if self.use_tokens:
            card = CreditCardData()
            card.token = amex_token

        response = (
            card.charge(17.04)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_014_charge_jcb(self):
        card = TestCards.jcb_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        response = (
            card.charge(17.05)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    # Credit Authorization

    def test_015_autorize_visa(self):
        # 015a authorization
        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "75024"

        response = (
            card.authorize(17.06)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        # 015b capture
        capture = response.capture().execute("ecommerce")

        self.assertNotEqual(None, capture)
        self.assertEqual("00", capture.response_code, capture.response_message)

    def test_016_autorize_mastercard(self):
        # 016a authorization
        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "750241234"

        response = (
            card.authorize(17.07)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        # 016b capture
        capture = response.capture().execute("ecommerce")

        self.assertNotEqual(None, capture)
        self.assertEqual("00", capture.response_code, capture.response_message)

    def test_017_autorize_discover(self):
        # 017a authorization
        card = TestCards.discover_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.authorize(17.08)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        # 017b capture
        # do not capture

    # Partially approved sale

    def test_018_partial_approval_visa(self):
        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(130)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_partial_auth(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("10", response.response_code, response.response_message)
        self.assertNotEqual(None, response.authorized_amount)
        self.assertEqual("110.00", response.authorized_amount)

    def test_019_partial_approval_discover(self):
        card = TestCards.discover_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(145)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_partial_auth(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("10", response.response_code, response.response_message)
        self.assertNotEqual(None, response.authorized_amount)
        self.assertEqual("65.00", response.authorized_amount)

    def test_020_partial_approval_mastercard(self):
        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(155)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_partial_auth(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("10", response.response_code, response.response_message)
        self.assertNotEqual(None, response.authorized_amount)
        self.assertEqual("100.00", response.authorized_amount)

    # Level II - Corporate Purchase Card

    def test_021_level_ii_response_b(self):
        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860 Dallas Pkwy"
        address.postal_code = "750241234"

        response = (
            card.charge(112.34)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("B", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.NotUsed)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_022_level_ii_response_b(self):
        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "750241234"

        response = (
            card.charge(112.34)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("B", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_tax_type(TaxType.SalesTax)
            .with_tax_amount(1.00)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_023_level_ii_response_r(self):
        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(123.45)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("R", response.commercial_indicator)

        cpc_response = (
            response.edit().with_tax_type(TaxType.TaxExempt).execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_024_level_ii_response_s(self):
        card = TestCards.visa_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(134.56)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("S", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_tax_type(TaxType.SalesTax)
            .with_tax_amount(1.00)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_025_level_ii_response_s(self):
        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.06)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("S", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.NotUsed)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_026_level_ii_response_s(self):
        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.07)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("S", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_tax_type(TaxType.SalesTax)
            .with_tax_amount(1.00)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_027_level_ii_response_s(self):
        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.08)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("S", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.SalesTax)
            .with_tax_amount(1.00)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_028_level_ii_response_s(self):
        card = TestCards.mastercard_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.09)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("S", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.TaxExempt)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_029_level_ii_no_response(self):
        card = TestCards.amex_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.10)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("0", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.NotUsed)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_030_level_ii_no_response(self):
        card = TestCards.amex_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.11)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("0", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_tax_type(TaxType.SalesTax)
            .with_tax_amount(1.00)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_031_level_ii_no_response(self):
        card = TestCards.amex_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.12)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("0", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.SalesTax)
            .with_tax_amount(1.00)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    def test_032_level_ii_no_response(self):
        card = TestCards.amex_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(111.13)
            .with_currency("USD")
            .with_address(address)
            .with_commercial_request(True)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("0", response.commercial_indicator)

        cpc_response = (
            response.edit()
            .with_po_number("9876543210")
            .with_tax_type(TaxType.TaxExempt)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, cpc_response)
        self.assertEqual(
            "00", cpc_response.response_code, cpc_response.response_message
        )

    # Prior / Voice authorization

    def test_033_offline_sale(self):
        card = TestCards.visa_manual()

        response = (
            card.charge(17.01)
            .with_currency("USD")
            .with_modifier(TransactionModifier.Offline)
            .with_offline_auth_code("654321")
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_033_offline_authorization(self):
        card = TestCards.visa_manual()

        response = (
            card.authorize(17.10)
            .with_currency("USD")
            .with_modifier(TransactionModifier.Offline)
            .with_offline_auth_code("654321")
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    # Offline return

    def test_034_offline_return(self):
        card = TestCards.visa_manual()

        response = (
            card.refund(15.15)
            .with_currency("USD")
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    # Online void / reversal

    def test_035_void_test_10(self):
        pass

    def test_036_void_test_20(self):
        pass

    # Advanced Fraud Screening

    @unittest.skip("AFS not configured")
    def test_037_fraud_prevention_sale(self):
        card = TestCards.visa_manual()

        response = (
            card.charge(15000)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("FR", response.response_code, response.response_message)

    @unittest.skip("AFS not configured")
    def test_038_fraud_prevention_return(self):
        card = TestCards.visa_manual()

        response = (
            card.refund(15000)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("41", response.response_code, response.response_message)

    # One Card / GSB / Prepaid

    @unittest.skipIf(use_prepaid == False, "ignore prepaid")
    def test_037_balance_inquiry_gsb(self):
        card = TestCards.gsb_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = card.balance_inquiry().with_address(address).execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    @unittest.skipIf(use_prepaid == False, "ignore prepaid")
    def test_038_add_value_gsb(self):
        card = CreditTrackData()
        card.value = "%B6277220572999800^   /                         ^49121010557010000016000000?F;6277220572999800=49121010557010000016?"

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.add_value(15.00)
            .with_currency("USD")
            .with_address(address)
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    @unittest.skipIf(use_prepaid == False, "ignore prepaid")
    def test_039_charge_gsb(self):
        card = TestCards.gsb_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(2.05)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        void_response = response.void().execute("ecommerce")

        self.assertNotEqual(None, void_response)
        self.assertEqual(
            "00", void_response.response_code, void_response.response_message
        )

    @unittest.skipIf(use_prepaid == False, "ignore prepaid")
    def test_040_charge_gsb(self):
        card = TestCards.gsb_manual()

        address = Address()
        address.street_address_1 = "6860"
        address.postal_code = "75024"

        response = (
            card.charge(2.10)
            .with_currency("USD")
            .with_address(address)
            .with_invoice_number("123456")
            .with_allow_duplicates(True)
            .execute("ecommerce")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    @unittest.skipIf(use_prepaid == False, "ignore prepaid")
    def test_041_void_gsb(self):
        pass

    # HMS Gift

    def test_042_activate_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.activate(6.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_043_activate_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.activate(7.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_044_add_value_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.add_value(8.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_045_add_value_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.add_value(9.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_046_balance_inquiry_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.balance_inquiry().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("10.00", response.balance_amount)

    def test_047_balance_inquiry_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.balance_inquiry().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("10.00", response.balance_amount)

    def test_048_replace_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.replace_with(TestCards.gift_card_2_manual()).execute(
            "ecommerce"
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_049_replace_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.replace_with(TestCards.gift_card_1_swipe()).execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_050_sale_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.charge(1.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_051_sale_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.charge(2.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_052_sale_gift_1_void(self):
        card = TestCards.gift_card_1_swipe()

        response = card.charge(1.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        void_response = response.void().execute("ecommerce")

        self.assertNotEqual(None, void_response)
        self.assertEqual(
            "00", void_response.response_code, void_response.response_message
        )

    def test_053_sale_gift_2_void(self):
        card = TestCards.gift_card_2_manual()

        response = card.charge(2.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        void_response = response.void().execute("ecommerce")

        self.assertNotEqual(None, void_response)
        self.assertEqual(
            "00", void_response.response_code, void_response.response_message
        )

    def test_054_void_gift(self):
        pass

    def test_055_reversal_gift_1(self):
        pass

    def test_056_reversal_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.charge(2.00).with_currency("USD").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

        # reverse based on card, not transaction id
        reverse_response = card.reverse(2.00).execute("ecommerce")

        self.assertNotEqual(None, reverse_response)
        self.assertEqual(
            "00", reverse_response.response_code, reverse_response.response_message
        )

    def test_057_deactivate_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.deactivate().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_058_receipts_messaging(self):
        pass

    # HMS Rewards

    def test_059_balance_inquiry_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.balance_inquiry().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("0", response.points_balance_amount)

    def test_060_balance_inquiry_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.balance_inquiry().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)
        self.assertEqual("0", response.points_balance_amount)

    def test_061_create_alias_gift_1(self):
        response = GiftCard.create("9725550100", "ecommerce")

        self.assertNotEqual(None, response)

    def test_062_create_alias_gift_2(self):
        response = GiftCard.create("9725550100", "ecommerce")

        self.assertNotEqual(None, response)

    def test_063_add_alias_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.add_alias("9725550100").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_064_add_alias_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.add_alias("9725550100").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_065_remove_alias_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.remove_alias("9725550100").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_066_redeem_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.charge(100).with_currency("points").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_067_redeem_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.charge(200).with_currency("points").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_068_redeem_rewards_2(self):
        card = GiftCard()
        card.alias = "9725550100"

        response = card.charge(300).with_currency("points").execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_069_reward_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.rewards(10).execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_070_reward_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.rewards(11).execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_071_replace_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.replace_with(TestCards.gift_card_2_manual()).execute(
            "ecommerce"
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_072_replace_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.replace_with(TestCards.gift_card_1_swipe()).execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_073_deactivate_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.deactivate().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_074_deactivate_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.deactivate().execute("ecommerce")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_075_receipts_messaging(self):
        pass

    def test_999_close_batch(self):
        try:
            response = BatchService.close_batch("ecommerce")
            self.assertNotEqual(None, response)
        except Exception as e:
            if (
                str(e.message).find(self.BATCH_NOT_OPEN) != -1
                or str(e.message).find(self.BATCH_EMPTY) != -1
            ):
                return
