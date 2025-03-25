"""
Test Credit
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import EncryptionData, Transaction, ThreeDSecure
from globalpayments.api.entities.enums import (
    ThreeDSecureVersion,
    StoredCredentialInitiator,
)
from globalpayments.api.payment_methods import CreditCardData, CreditTrackData


class IntegrationGatewaysPorticoConnectorCreditTests(unittest.TestCase):
    """
    Ensure credit transactions work
    """

    config = PorticoConfig()
    config.secret_api_key = "skapi_cert_MTeSAQAfG1UA9qQDrzl-kz4toXvARyieptFwSKP24w"
    config.service_url = "https://cert.api2.heartlandportico.com"
    config.developer_id = "000000"
    config.version_number = "0000"

    ServicesContainer.configure(config)

    card = CreditCardData()
    card.number = "4111111111111111"
    card.exp_month = "12"
    card.exp_year = "2025"
    card.cvn = "123"
    card.card_holder_name = "Joe Smith"

    track = CreditTrackData()
    track.value = "<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|LO04K0WFOmdkDz0um+GwUkILL8ZZOP6Zc4rCpZ9+kg2T3JBT4AEOilWTI|+++++++Dbbn04ekG|11;4012001000000016=25120000000000000000?|1u2F/aEhbdoPixyAPGyIDv3gBfF|+++++++Dbbn04ekG|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>;"
    track.encryption_data = EncryptionData()
    track.encryption_data.version = "01"

    def test_credit_auth(self):
        response = (
            self.card.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        capture = response.capture(16).with_gratuity(2).execute()

        self.assertNotEqual(None, capture)
        self.assertEqual("00", capture.response_code)

    def test_credit_auth_with_convenience(self):
        response = (
            self.card.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_auth_with_shipping(self):
        response = (
            self.card.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_sale(self):
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_sale_with_convenience(self):
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_sale_with_shipping(self):
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_offline_auth(self):
        response = (
            self.card.authorize(16)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_offline_auth_with_convenience(self):
        response = (
            self.card.authorize(16)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_offline_auth_with_shipping(self):
        response = (
            self.card.authorize(16)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_offline_sale(self):
        response = (
            self.card.charge(17)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_offline_sale_with_convenience(self):
        response = (
            self.card.charge(17)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_offline_sale_with_shipping(self):
        response = (
            self.card.charge(17)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_refund(self):
        response = (
            self.card.refund(16)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_reverse(self):
        response = self.card.reverse(15).with_allow_duplicates(True).execute()

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_auth(self):
        response = (
            self.track.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        capture = response.capture(16).with_gratuity(2).execute()

        self.assertNotEqual(None, capture)
        self.assertEqual("00", capture.response_code)

    def test_credit_swipe_auth_with_convenience(self):
        response = (
            self.track.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_auth_with_shipping(self):
        response = (
            self.track.authorize(14)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_sale(self):
        response = (
            self.track.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_sale_with_convenience(self):
        response = (
            self.track.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_sale_with_shipping(self):
        response = (
            self.track.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_offline_auth(self):
        response = (
            self.track.authorize(16)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_offline_auth_with_convenience(self):
        response = (
            self.track.authorize(16)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_offline_auth_with_shipping(self):
        response = (
            self.track.authorize(16)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_offline_sale(self):
        response = (
            self.track.charge(17)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_offline_sale_with_convenience(self):
        response = (
            self.track.charge(17)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_convenience_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_offline_sale_with_shipping(self):
        response = (
            self.track.charge(17)
            .with_currency("USD")
            .with_offline_auth_code("123456")
            .with_allow_duplicates(True)
            .with_shipping_amt(2)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_balance_inquiry(self):
        response = self.track.balance_inquiry().execute()

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_refund(self):
        response = (
            self.track.refund(16)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_swipe_reverse(self):
        response = (
            self.track.charge(19)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        reverse_response = self.track.reverse(15).with_allow_duplicates(True).execute()

        self.assertNotEqual(None, reverse_response)
        self.assertEqual("00", reverse_response.response_code)

    def test_credit_swipe_verify(self):
        response = self.track.verify().with_allow_duplicates(True).execute()

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_void_from_transaction_id(self):
        response = (
            self.card.authorize(10)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

        void_response = Transaction.from_id(response.transaction_id).void().execute()

        self.assertNotEqual(None, void_response)
        self.assertEqual("00", void_response.response_code)

    def test_check_crypto_gold_standard(self):
        gold_config = PorticoConfig()
        gold_config.secret_api_key = (
            "skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A"
        )
        gold_config.service_url = "https://cert.api2-c.heartlandportico.com"

        ServicesContainer.configure(gold_config, "gold standard")
        response = (
            self.card.authorize(10)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("gold standard")
        )
        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_legacy_portico_creds(self):
        legacy_config = PorticoConfig()
        legacy_config.license_id = 375032
        legacy_config.site_id = 375247
        legacy_config.device_id = 7381760
        legacy_config.username = "777703756680"
        legacy_config.password = "78SVw5TrJ4xRi4$"
        legacy_config.service_url = "https://cert.api2.heartlandportico.com"
        legacy_config.developer_id = "000000"
        legacy_config.version_number = "0000"

        ServicesContainer.configure(legacy_config, "legacy_config")

        response = (
            self.card.authorize(10)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .execute("legacy_config")
        )
        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_3dSecure_v1(self):
        ecom = ThreeDSecure()
        ecom.cavv = "XXXXf98AAajXbDRg3HSUMAACAAA="
        ecom.xid = "0l35fwh1sys3ojzyxelu4ddhmnu5zfke5vst"
        ecom.eci = 5
        ecom.version = ThreeDSecureVersion.One
        self.card.three_d_secure = ecom
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_invoice_number("1234567890")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_3dSecure_v2(self):
        ecom = ThreeDSecure()
        ecom.cavv = "XXXXf98AAajXbDRg3HSUMAACAAA="
        ecom.xid = "0l35fwh1sys3ojzyxelu4ddhmnu5zfke5vst"
        ecom.eci = 5
        ecom.version = ThreeDSecureVersion.Two
        self.card.three_d_secure = ecom
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_invoice_number("1234567890")
            .with_allow_duplicates(True)
            .execute()
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_credit_sale_with_cof(self):
        # First transaction - initial card holder initiated transaction
        response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_card_brand_storage(StoredCredentialInitiator.CardHolder)
            .execute()
        )
        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)
        self.assertNotEqual(None, response.card_brand_transaction_id)

        # Second transaction - merchant initiated transaction using stored credentials
        cof_response = (
            self.card.charge(15)
            .with_currency("USD")
            .with_allow_duplicates(True)
            .with_card_brand_storage(
                StoredCredentialInitiator.Merchant, response.card_brand_transaction_id
            )
            .execute()
        )
        self.assertNotEqual(None, cof_response)
        self.assertEqual("00", cof_response.response_code)
