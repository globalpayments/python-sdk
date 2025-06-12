import unittest

from globalpayments.api import ServicesContainer
from globalpayments.api.entities import EncryptionData
from globalpayments.api.entities.enums import CardChannel, EntryMethod
from globalpayments.api.entities.exceptions import GatewayException
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.payment_methods import DebitTrackData
from tests.data.GpApi_test_config import GpApiTestConfig


class GpApiDebitTest(unittest.TestCase):
    """
    Test debit card transactions with GpApi
    """

    def setUp(self):
        # Reset configuration before each test
        config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_PRESENT)
        ServicesContainer.configure(config)

        # Setup test data
        self.amount = "12.02"
        self.currency = "USD"

        # Setup debit track data
        self.debit_track_data = DebitTrackData()
        self.debit_track_data.value = "%B4012002000060016^VI TEST CREDIT^251210118039000000000396?;4012002000060016=25121011803939600000?"
        self.debit_track_data.pin_block = "32539F50C245A6A93D123412324000AA"
        self.debit_track_data.entry_method = EntryMethod.Swipe

        # Tag data for chip transactions
        self.tag_data = "9F4005F000F0A0019F02060000000025009F03060000000000009F2608D90A06501B48564E82027C005F3401019F360200029F0702FF009F0802008C9F0902008C9F34030403029F2701809F0D05F0400088009F0E0508000000009F0F05F0400098005F280208409F390105FFC605DC4000A800FFC7050010000000FFC805DC4004F8009F3303E0B8C89F1A0208409F350122950500000080005F2A0208409A031409109B02E8009F21030811539C01009F37045EED3A8E4F07A00000000310109F0607A00000000310108407A00000000310109F100706010A03A400029F410400000001"

    def assert_transaction_response(self, response, expected_status):
        self.assertIsNotNone(response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(expected_status, response.response_message)

    def test_debit_sale_swipe(self):
        response = (
            self.debit_track_data.charge(self.amount)
            .with_currency(self.currency)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    def test_debit_sale_swipe_chip(self):
        response = (
            self.debit_track_data.charge(self.amount)
            .with_currency(self.currency)
            .with_tag_data(self.tag_data)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    def test_debit_sale_swipe_authorize_then_capture(self):
        response = (
            self.debit_track_data.authorize(self.amount)
            .with_currency(self.currency)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.PREAUTHORIZED)

        capture_response = (
            response.capture(self.amount).with_currency(self.currency).execute()
        )
        self.assert_transaction_response(capture_response, TransactionStatus.CAPTURED)

    def test_debit_refund_swipe(self):
        response = (
            self.debit_track_data.refund(self.amount)
            .with_currency(self.currency)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    def test_debit_refund_chip(self):
        self.debit_track_data.pin_block = None

        response = (
            self.debit_track_data.refund(self.amount)
            .with_currency(self.currency)
            .with_tag_data(self.tag_data)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    @unittest.skip("Skipping this test - server error")
    def test_debit_sale_swipe_encrypted(self):
        self.debit_track_data.value = "<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|LO04K0WFOmdkDz0um+GwUkILL8ZZOP6Zc4rCpZ9+kg2T3JBT4AEOilWTI|+++++++Dbbn04ekG|11;4012001000000016=25120000000000000000?|1u2F/aEhbdoPixyAPGyIDv3gBfF|+++++++Dbbn04ekG|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>"
        self.debit_track_data.encryption_data = EncryptionData.version_1()

        response = (
            self.debit_track_data.charge(self.amount)
            .with_currency(self.currency)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    def test_debit_sale_swipe_chip_new_debit_track_data_details(self):
        track_data = DebitTrackData()
        track_data.value = ";4024720012345671=18125025432198712345?"
        track_data.pin_block = "AFEC374574FC90623D010000116001EE"
        track_data.entry_method = EntryMethod.Swipe

        tag_data = "82021C008407A0000002771010950580000000009A031709289C01005F280201245F2A0201245F3401019F02060000000010009F03060000000000009F080200019F090200019F100706010A03A420009F1A0201249F26089CC473F4A4CE18D39F2701809F3303E0F8C89F34030100029F3501229F360200639F370435EFED379F410400000019"

        response = (
            track_data.charge(self.amount)
            .with_currency(self.currency)
            .with_tag_data(tag_data)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    def test_debit_sale_contactless_chip_new_debit_track_data_details(self):
        track_data = DebitTrackData()
        track_data.value = ";4024720012345671=18125025432198712345?"
        track_data.pin_block = "AFEC374574FC90623D010000116001EE"
        track_data.entry_method = EntryMethod.Proximity

        tag_data = "82021C008407A0000002771010950580000000009A031709289C01005F280201245F2A0201245F3401019F02060000000010009F03060000000000009F080200019F090200019F100706010A03A420009F1A0201249F26089CC473F4A4CE18D39F2701809F3303E0F8C89F34030100029F3501229F360200639F370435EFED379F410400000019"

        response = (
            track_data.charge(self.amount)
            .with_currency(self.currency)
            .with_tag_data(tag_data)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

    def test_debit_swipe_reverse(self):
        response = (
            self.debit_track_data.charge(self.amount)
            .with_currency(self.currency)
            .execute()
        )
        self.assert_transaction_response(response, TransactionStatus.CAPTURED)

        reverse = response.reverse(self.amount).execute()
        self.assert_transaction_response(reverse, TransactionStatus.REVERSED)

    @unittest.skip("Skipping this test - server error")
    def test_debit_refund_chip_rejected(self):
        exception_caught = False
        try:
            self.debit_track_data.refund(self.amount).with_currency(
                self.currency
            ).with_tag_data(self.tag_data).execute()
        except GatewayException as ex:
            exception_caught = True
            self.assertEqual("40029", ex.response_code)
        finally:
            self.assertTrue(exception_caught)
