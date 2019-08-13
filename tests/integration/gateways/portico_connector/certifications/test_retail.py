'''
Test retail
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities import Address
from globalpayments.api.entities.enums import EntryMethod, InquiryType, TaxType, TransactionModifier
from globalpayments.api.payment_methods import CreditCardData, GiftCard
from globalpayments.api.services import BatchService
from data import TestCards

visa_token = None
mastercard_token = None
discover_token = None
amex_token = None


class IntegrationGatewaysPorticoConnectorCertificationRetailTests(
        unittest.TestCase):
    '''
    Ensure retail transactions work
    '''

    BATCH_NOT_OPEN = 'Transaction was rejected because it requires a batch to be open.'
    BATCH_EMPTY = 'Batch close was rejected because no transactions are associated with the currently open batch'

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MaePAQBr-1QAqjfckFC8FTbRTT120bVQUlfVOjgCBw'
    config.service_url = 'https://cert.api2.heartlandportico.com'
    config.developer_id = '000000'
    config.version_number = '0000'

    ServicesContainer.configure(config, 'retail')

    use_tokens = False

    def test_000_close_batch(self):
        try:
            response = BatchService.close_batch('retail')
            self.assertNotEqual(None, response)
        except Exception as e:
            if str(e.message).find(self.BATCH_NOT_OPEN) != -1 or str(
                    e.message).find(self.BATCH_EMPTY) != -1:
                return

    # Card Verify

    def test_001_card_verify_visa(self):
        visa_enc = TestCards.visa_swipe_encrypted()

        response = visa_enc.verify() \
                   .with_request_multi_use_token(self.use_tokens) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        if self.use_tokens:
            self.assertNotEqual(None, response.token)

            token = CreditCardData()
            token.token = response.token

            sale_response = token.charge(15.01) \
                            .with_allow_duplicates(True) \
                            .execute('retail')

            self.assertNotEqual(None, sale_response)
            self.assertEqual('00', sale_response.response_code,
                             sale_response.response_message)

    def test_002_card_verify_mastercard(self):
        mastercard_enc = TestCards.mastercard_swipe_encrypted()

        response = mastercard_enc.verify() \
                   .with_request_multi_use_token(self.use_tokens) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        if self.use_tokens:
            self.assertNotEqual(None, response.token)

            token = CreditCardData()
            token.token = response.token

            sale_response = token.charge(15.02) \
                            .with_allow_duplicates(True) \
                            .execute('retail')

            self.assertNotEqual(None, sale_response)
            self.assertEqual('00', sale_response.response_code,
                             sale_response.response_message)

    def test_003_card_verify_discover(self):
        discover_enc = TestCards.discover_swipe_encrypted()

        response = discover_enc.verify() \
                   .with_request_multi_use_token(self.use_tokens) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        if self.use_tokens:
            self.assertNotEqual(None, response.token)

            token = CreditCardData()
            token.token = response.token

            sale_response = token.charge(15.03) \
                            .with_allow_duplicates(True) \
                            .execute('retail')

            self.assertNotEqual(None, sale_response)
            self.assertEqual('00', sale_response.response_code,
                             sale_response.response_message)

    # Account Verification

    def test_004_card_verify_amex(self):
        address = Address()
        address.postal_code = '75024'
        amex = TestCards.amex_swipe()

        response = amex.verify() \
                   .with_request_multi_use_token(self.use_tokens) \
                   .with_address(address) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        if self.use_tokens:
            self.assertNotEqual(None, response.token)

            token = CreditCardData()
            token.token = response.token

            sale_response = token.charge(15.04) \
                            .with_allow_duplicates(True) \
                            .execute('retail')

            self.assertNotEqual(None, sale_response)
            self.assertEqual('00', sale_response.response_code,
                             sale_response.response_message)

    def test_005_balance_inquiry_visa(self):
        visa_enc = TestCards.visa_swipe_encrypted()

        response = visa_enc.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Credit Sale (for multi-use token only)

    def test_006_charge_visa_swipe_token(self):
        global visa_token

        card = TestCards.visa_swipe()

        response = card.charge(15.01) \
                   .with_currency('USD') \
                   .with_request_multi_use_token(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertNotEqual(None, response.token)

        visa_token = response.token

    def test_007_charge_mastercard_swipe_token(self):
        global mastercard_token

        card = TestCards.mastercard_swipe()

        response = card.charge(15.02) \
                   .with_currency('USD') \
                   .with_request_multi_use_token(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertNotEqual(None, response.token)

        mastercard_token = response.token

    def test_008_charge_discover_swipe_token(self):
        global discover_token

        card = TestCards.discover_swipe()

        response = card.charge(15.03) \
                   .with_currency('USD') \
                   .with_request_multi_use_token(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertNotEqual(None, response.token)

        discover_token = response.token

    def test_009_charge_amex_swipe_token(self):
        global amex_token

        card = TestCards.amex_swipe()

        response = card.charge(15.04) \
                   .with_currency('USD') \
                   .with_request_multi_use_token(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertNotEqual(None, response.token)

        amex_token = response.token

    def test_010_charge_visa_swipe(self):
        card = TestCards.visa_swipe()

        response = card.charge(15.01) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 59
        reverse = response.reverse(15.01).execute('retail')

        self.assertNotEqual(None, reverse)
        self.assertEqual('00', reverse.response_code, reverse.response_message)

    def test_011_charge_mastercard_swipe(self):
        card = TestCards.mastercard_swipe()

        response = card.charge(15.02) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_012_charge_discover_swipe(self):
        card = TestCards.discover_swipe()

        response = card.charge(15.03) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_013_charge_amex_swipe(self):
        card = TestCards.amex_swipe()

        response = card.charge(15.04) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_014_charge_jcb_swipe(self):
        card = TestCards.jcb_swipe()

        response = card.charge(15.05) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 58

        refund = response.refund(15.05) \
                 .with_currency('USD') \
                 .execute('retail')

        self.assertNotEqual(None, refund)
        self.assertEqual('00', refund.response_code, refund.response_message)

    def test_014a_charge_mastercard_24_swipe(self):
        card = TestCards.mastercard_24_swipe()

        response = card.charge(15.34) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_014b_charge_mastercard_25_swipe(self):
        card = TestCards.mastercard_swipe()

        response = card.charge(15.34) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_015_charge_visa_manual_card_present(self):
        address = Address()
        address.postal_code = '750241234'
        address.street_address_1 = '6860 Dallas Pkwy'
        card = TestCards.visa_manual(True, True)

        response = card.charge(16.01) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Manually entered - card present

    def test_016_charge_visa_manual_card_present(self):
        address = Address()
        address.postal_code = '750241234'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.visa_manual(True, True)

        response = card.charge(16.01) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_017_charge_mastercard_manual_card_present(self):
        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.mastercard_manual(True, True)

        response = card.charge(16.02) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_018_charge_discover_manual_card_present(self):
        address = Address()
        address.postal_code = '750241234'

        card = TestCards.discover_manual(True, True)

        response = card.charge(16.03) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_019_charge_amex_manual_card_present(self):
        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860'

        card = TestCards.amex_manual(True, True)

        response = card.charge(16.04) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_020_charge_jcb_manual_card_present(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.jcb_manual(True, True)

        response = card.charge(16.05) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_021_charge_discover_manual_card_present(self):
        address = Address()
        address.postal_code = '750241234'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.discover_manual(True, True)

        response = card.charge(16.07) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 64
        reversal = response.reverse(16.07) \
                   .with_auth_amount(6.07) \
                   .execute('retail')

        self.assertNotEqual(None, reversal)
        self.assertEqual('00', reversal.response_code,
                         reversal.response_message)

    # Manually entered - card not present

    def test_022_charge_visa_manual_card_not_present(self):
        global visa_token

        address = Address()
        address.postal_code = '750241234'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = None
        if self.use_tokens:
            card = CreditCardData()
            card.token = visa_token
        else:
            card = TestCards.visa_manual(False, True)

        response = card.charge(17.01) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_023_charge_mastercard_manual_card_not_present(self):
        global mastercard_token

        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = None
        if self.use_tokens:
            card = CreditCardData()
            card.token = mastercard_token
        else:
            card = TestCards.mastercard_manual(False, True)

        response = card.charge(17.02) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 61
        reversal = response.reverse(17.02).execute('retail')

        self.assertNotEqual(None, reversal)
        self.assertEqual('00', reversal.response_code,
                         reversal.response_message)

    def test_024_charge_discover_manual_card_not_present(self):
        global discover_token

        address = Address()
        address.postal_code = '750241234'

        card = None
        if self.use_tokens:
            card = CreditCardData()
            card.token = discover_token
        else:
            card = TestCards.discover_manual(False, True)

        response = card.charge(17.03) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_025_charge_amex_manual_card_not_present(self):
        global amex_token

        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860'

        card = None
        if self.use_tokens:
            card = CreditCardData()
            card.token = amex_token
        else:
            card = TestCards.amex_manual(False, True)

        response = card.charge(17.04) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_026_charge_jcb_manual_card_not_present(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.jcb_manual(False, True)

        response = card.charge(17.05) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Contactless

    def test_027_charge_visa_contactless(self):
        card = TestCards.visa_swipe(EntryMethod.Proximity)

        response = card.charge(18.01) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_028_charge_mastercard_contactless(self):
        card = TestCards.mastercard_swipe(EntryMethod.Proximity)

        response = card.charge(18.02) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_029_charge_discover_contactless(self):
        card = TestCards.discover_swipe(EntryMethod.Proximity)

        response = card.charge(18.03) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_030_charge_amex_contactless(self):
        card = TestCards.amex_swipe(EntryMethod.Proximity)

        response = card.charge(18.04) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Authorization

    def test_031_authorize_visa_swipe(self):
        card = TestCards.visa_swipe()

        # 031a authorize
        response = card.authorize(15.08) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 031b capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_032_authorize_visa_swipe_additional_auth(self):
        card = TestCards.visa_swipe()

        # 032a authorize
        response = card.authorize(15.09) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 032b additional auth (restaurant only)

        # 032c add to batch
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_033_authorize_mastercard_swipe(self):
        card = TestCards.mastercard_swipe()

        # 033a authorize
        response = card.authorize(15.08) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 033b capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_033a_authorize_discover_swipe(self):
        card = TestCards.discover_swipe()

        response = card.authorize(15.10) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Authorization - manually entered, card present

    def test_034_authorize_visa_manual_card_present(self):
        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.visa_manual(True, True)

        # 034a authorize
        response = card.authorize(16.08) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 034b capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_035_authorize_visa_manual_card_present_additional_auth(self):
        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.visa_manual(True, True)

        # 035a authorize
        response = card.authorize(16.09) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 035b additional auth (restaurant only)

        # 035c capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_036_authorize_mastercard_manual_card_present(self):
        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.mastercard_manual(True, True)

        # 036a authorize
        response = card.authorize(16.10) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 036b capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_036a_authorize_discover_manual_card_present(self):
        address = Address()
        address.postal_code = '750241234'

        card = TestCards.discover_manual(True, True)

        response = card.authorize(16.10) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Authorization - manually entered, card not present

    def test_037_authorize_visa_manual(self):
        address = Address()
        address.postal_code = '750241234'
        address.street_address_1 = '6860 Dallas Pkwy'

        card = TestCards.visa_manual(False, True)

        # 037a authorize
        response = card.authorize(17.08) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 037b capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_038_authorize_mastercard_manual(self):
        address = Address()
        address.postal_code = '75024'
        address.street_address_1 = '6860'

        card = TestCards.mastercard_manual(False, True)

        # 038a authorize
        response = card.authorize(17.09) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # 038b capture
        capture_response = response.capture().execute('retail')

        self.assertNotEqual(None, capture_response)
        self.assertEqual('00', capture_response.response_code,
                         capture_response.response_message)

    def test_039_authorize_discover_manual(self):
        address = Address()
        address.postal_code = '750241234'

        card = TestCards.discover_manual(False, True)

        response = card.authorize(17.10) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Parially approved sale (required)

    def test_039_charge_discover_swipe_partial_approval(self):
        card = TestCards.discover_swipe()

        response = card.charge(40.00) \
                   .with_currency('USD') \
                   .with_allow_partial_auth(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('10', response.response_code,
                         response.response_message)
        self.assertEqual('40.00', response.authorized_amount)

    def test_040_charge_visa_swipe_partial_approval(self):
        card = TestCards.visa_swipe()

        response = card.charge(130.00) \
                   .with_currency('USD') \
                   .with_allow_partial_auth(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('10', response.response_code,
                         response.response_message)
        self.assertEqual('110.00', response.authorized_amount)

    def test_041_charge_discover_manual_partial_approval(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.discover_manual()

        response = card.charge(145.00) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_partial_auth(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('10', response.response_code,
                         response.response_message)
        self.assertEqual('65.00', response.authorized_amount)

    def test_042_charge_mastercard_swipe_partial_approval(self):
        card = TestCards.mastercard_swipe()

        response = card.charge(155.00) \
                   .with_currency('USD') \
                   .with_allow_partial_auth(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('10', response.response_code,
                         response.response_message)
        self.assertEqual('100.00', response.authorized_amount)

        # test case 62
        reversal = response.reverse(100.00).execute('retail')

        self.assertNotEqual(None, reversal)
        self.assertEqual('00', reversal.response_code,
                         reversal.response_message)

    # Sale with gratuity - tip edit (tip at settlement)

    def test_043_charge_visa_swipe_edit_gratuity(self):
        card = TestCards.visa_swipe()

        response = card.charge(15.12) \
                   .with_currency('USD') \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        edit_response = response.edit() \
                        .with_amount(18.12) \
                        .with_gratuity(3.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_044_charge_mastercard_manual_edit_gratuity(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.mastercard_manual(True, True)

        response = card.charge(15.13) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        edit_response = response.edit() \
                        .with_amount(18.13) \
                        .with_gratuity(3.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    # Tip on purchase

    def test_045_charge_visa_manual_gratuity(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.visa_manual(True, True)

        response = card.charge(18.61) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_gratuity(3.50) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_046_charge_mastercard_swipe_gratuity(self):
        card = TestCards.mastercard_swipe()

        response = card.charge(18.62) \
                   .with_currency('USD') \
                   .with_gratuity(3.50) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        edit_response = response.edit() \
                        .with_amount(18.12) \
                        .with_gratuity(3.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    # Level II corporate purchase card

    def test_047_level_ii_visa_swipe_response_b(self):
        card = TestCards.visa_swipe()

        response = card.charge(112.34) \
                   .with_currency('USD') \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('B', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_tax_type(TaxType.SalesTax) \
                        .with_tax_amount(1.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    @unittest.skip('gateway doesn\'t return correct response code')
    def test_047a_level_ii_visa_swipe_response_b(self):
        card = TestCards.visa_swipe()

        response = card.charge(112.35) \
                   .with_currency('USD') \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('B', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_tax_type(TaxType.NotUsed) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_048_level_ii_visa_swipe_response_r(self):
        card = TestCards.visa_swipe()

        response = card.charge(123.45) \
                   .with_currency('USD') \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('R', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_tax_type(TaxType.TaxExempt) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_049_level_ii_visa_manual_response_s(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.visa_manual(True, True)

        response = card.charge(134.56) \
                   .with_currency('USD') \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('S', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.SalesTax) \
                        .with_tax_amount(1.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_050_level_ii_mastercard_swipe_response_s(self):
        card = TestCards.mastercard_swipe()

        response = card.charge(111.06) \
                   .with_currency('USD') \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('S', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.NotUsed) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_051_level_ii_mastercard_manual_response_s(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.mastercard_manual(True, True)

        response = card.charge(111.07) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('S', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.SalesTax) \
                        .with_tax_amount(1.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_051a_level_ii_mastercard_manual_response_s(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.mastercard_manual(True, True)

        response = card.charge(111.08) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('S', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.SalesTax) \
                        .with_tax_amount(1.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_052_level_ii_mastercard_manual_response_s(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.mastercard_manual(True, True)

        response = card.charge(111.09) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('S', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.TaxExempt) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_053_level_ii_amex_swipe_no_response(self):
        card = TestCards.amex_swipe()

        response = card.charge(111.10) \
                   .with_currency('USD') \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('0', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_tax_type(TaxType.SalesTax) \
                        .with_tax_amount(1.00) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_054_level_ii_amex_manual_no_response(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.amex_manual(True, True)

        response = card.charge(111.11) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('0', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.NotUsed) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_055_level_ii_amex_manual_no_response(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.amex_manual(True, True)

        response = card.charge(111.12) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('0', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.NotUsed) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    def test_055a_level_ii_amex_manual_no_response(self):
        address = Address()
        address.postal_code = '75024'

        card = TestCards.amex_manual(True, True)

        response = card.charge(111.13) \
                   .with_currency('USD') \
                   .with_address(address) \
                   .with_commercial_request(True) \
                   .with_allow_duplicates(True) \
                   .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('0', response.commercial_indicator)

        edit_response = response.edit() \
                        .with_po_number('9876543210') \
                        .with_tax_type(TaxType.TaxExempt) \
                        .execute('retail')

        self.assertNotEqual(None, edit_response)
        self.assertEqual('00', edit_response.response_code,
                         edit_response.response_message)

    # Offline sale / authorization

    def test_056_offline_charge_visa_manual(self):
        card = TestCards.visa_manual(False, True)

        response = card.charge(15.12) \
                        .with_currency('USD') \
                        .with_offline_auth_code('654321') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_056_offline_auth_visa_manual(self):
        card = TestCards.visa_manual(False, True)

        response = card.authorize(15.11) \
                        .with_currency('USD') \
                        .with_offline_auth_code('654321') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # return

    def test_057_return_mastercard(self):
        card = TestCards.mastercard_manual(False, True)

        response = card.refund(15.11) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_057a_return_mastercard_swipe(self):
        card = TestCards.mastercard_swipe()

        response = card.refund(15.15) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Online void / reversal (required)

    # Pin debit card functions

    def test_065_debit_sale_visa_swipe(self):
        card = TestCards.as_debit(TestCards.visa_swipe(),
                                  '32539F50C245A6A93D123412324000AA')

        response = card.charge(14.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_066_debit_sale_mastercard_swipe(self):
        card = TestCards.as_debit(TestCards.mastercard_swipe(),
                                  'F505AD81659AA42A3D123412324000AB')

        response = card.charge(14.02) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 71
        reversal = card.reverse(14.02).execute('retail')

        self.assertNotEqual(None, reversal)
        self.assertEqual('00', reversal.response_code,
                         reversal.response_message)

    def test_067_debit_sale_visa_swipe(self):
        card = TestCards.as_debit(TestCards.visa_swipe(),
                                  '32539F50C245A6A93D123412324000AA')

        response = card.charge(14.03) \
                        .with_currency('USD') \
                        .with_cash_back(5.00) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_067a_debit_sale_mastercard_swipe(self):
        card = TestCards.as_debit(TestCards.mastercard_swipe(),
                                  'F505AD81659AA42A3D123412324000AB')

        response = card.charge(14.04) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Partially approved purchase

    def test_068_debit_sale_mastercard_swipe_partial_approval(self):
        card = TestCards.as_debit(TestCards.mastercard_swipe(),
                                  'F505AD81659AA42A3D123412324000AB')

        response = card.charge(33.00) \
                        .with_currency('USD') \
                        .with_allow_partial_auth(True) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('10', response.response_code,
                         response.response_message)
        self.assertEqual('22.00', response.authorized_amount)

    def test_069_debit_sale_visa_swipe_partial_approval(self):
        card = TestCards.as_debit(TestCards.visa_swipe(),
                                  '32539F50C245A6A93D123412324000AA')

        response = card.charge(44.00) \
                        .with_currency('USD') \
                        .with_allow_partial_auth(True) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('10', response.response_code,
                         response.response_message)
        self.assertEqual('33.00', response.authorized_amount)

        # test case 72
        reversal = card.reverse(33).execute('retail')

        self.assertNotEqual(None, reversal)
        self.assertEqual('00', reversal.response_code,
                         reversal.response_message)

    # return

    def test_070_debit_return_visa_swipe(self):
        card = TestCards.as_debit(TestCards.visa_swipe(),
                                  '32539F50C245A6A93D123412324000AA')

        response = card.refund(14.07) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_070a_debit_return_visa_swipe(self):
        card = TestCards.as_debit(TestCards.visa_swipe(),
                                  '32539F50C245A6A93D123412324000AA')

        response = card.refund(14.08) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        reversal = card.reverse(14.08).execute('retail')

        self.assertNotEqual(None, reversal)
        self.assertEqual('00', reversal.response_code,
                         reversal.response_message)

    # Reversal

    # EBT functions - Food stamp purchase

    def test_080_ebtfs_purchase_visa_swipe(self):
        card = TestCards.as_ebt(TestCards.visa_swipe(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.charge(101.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_081_ebtfs_purchase_visa_manual(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(False, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.charge(102.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Food stamp electronic voucher (manual entry only)

    def test_082_ebt_voucher_purchase_visa_manual(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(False, True),
            '32539F50C245A6A93D123412324000AA')
        card.serial_number = '123456789012345'
        card.approval_code = '123456'

        response = card.charge(103.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Food stamp return

    def test_083_ebtfs_return_visa_swipe(self):
        card = TestCards.as_ebt(TestCards.visa_swipe_encrypted(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.refund(104.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_084_ebtfs_return_visa_manual(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(False, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.refund(105.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Food stamp balance inquiry

    def test_085_ebt_balance_inquiry_visa_swipe(self):
        card = TestCards.as_ebt(TestCards.visa_swipe_encrypted(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_086_ebt_balance_inquiry_visa_manual(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(True, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # EBT cash benefits - cash back purchase

    def test_087_ebt_cash_back_purchase_visa_swipe(self):
        card = TestCards.as_ebt(TestCards.visa_swipe(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.charge(106.01) \
                        .with_currency('USD') \
                        .with_cash_back(5.00) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_088_ebt_cash_back_purchase_visa_manual(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(False, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.charge(107.01) \
                        .with_currency('USD') \
                        .with_cash_back(5.00) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # No cash back

    def test_089_ebt_cash_back_purchase_visa_swipe_no_cash_back(self):
        card = TestCards.as_ebt(TestCards.visa_swipe(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.charge(108.01) \
                        .with_currency('USD') \
                        .with_cash_back(0) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_090_ebt_cash_back_purchase_visa_manual_no_cash_back(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(False, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.charge(109.01) \
                        .with_currency('USD') \
                        .with_cash_back(0) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Cash back balance inquiry

    def test_091_ebt_balance_inquiry_visa_swipe_cash(self):
        card = TestCards.as_ebt(TestCards.visa_swipe_encrypted(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.balance_inquiry(InquiryType.Cash).execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_092_ebt_balance_inquiry_visa_manual_cash(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(True, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.balance_inquiry(InquiryType.Cash).execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # Cash benefits

    def test_093_ebt_benefit_withdrawal_visa_swipe(self):
        card = TestCards.as_ebt(TestCards.visa_swipe(),
                                '32539F50C245A6A93D123412324000AA')

        response = card.charge(110.01) \
                        .with_currency('USD') \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_094_ebt_benefit_withdrawal_visa_manual(self):
        card = TestCards.as_ebt(
            TestCards.visa_manual(False, True),
            '32539F50C245A6A93D123412324000AA')

        response = card.charge(111.01) \
                        .with_currency('USD') \
                        .with_cash_back(0) \
                        .with_allow_duplicates(True) \
                        .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # HMS Gift

    def test_095_activate_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.activate(6.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_096_activate_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.activate(7.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_097_add_value_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.add_value(8.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_098_add_value_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.add_value(9.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_099_balance_inquiry_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('10.00', response.balance_amount)

    def test_100_balance_inquiry_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('10.00', response.balance_amount)

    def test_101_replace_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.replace_with(
            TestCards.gift_card_2_manual()).execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_102_replace_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.replace_with(
            TestCards.gift_card_1_swipe()).execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_103_sale_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.charge(1.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_104_sale_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.charge(2.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_105_sale_gift_1_void(self):
        card = TestCards.gift_card_1_swipe()

        response = card.charge(3.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 107
        void_response = response.void().execute('retail')

        self.assertNotEqual(None, void_response)
        self.assertEqual('00', void_response.response_code,
                         void_response.response_message)

    def test_106_sale_reversal_gift_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.charge(4.00) \
            .with_currency('USD') \
            .execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 108
        reverse_response = response.reverse(4.00).execute('retail')

        self.assertNotEqual(None, reverse_response)
        self.assertEqual('00', reverse_response.response_code,
                         reverse_response.response_message)

    def test_107_void_gift(self):
        pass

    def test_108_reversal_gift_1(self):
        pass

    def test_109_deactivate_gift_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.deactivate().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_110_receipts_messaging(self):
        pass

    # HMS Rewards

    def test_111_balance_inquiry_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('0', response.points_balance_amount)

    def test_112_balance_inquiry_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.balance_inquiry().execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
        self.assertEqual('0', response.points_balance_amount)

    def test_113_create_alias_gift_1(self):
        response = GiftCard.create('9725550100', 'ecommerce')

        self.assertNotEqual(None, response)

    def test_114_create_alias_gift_2(self):
        response = GiftCard.create('9725550100', 'ecommerce')

        self.assertNotEqual(None, response)

    def test_115_add_alias_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.add_alias('9725550100').execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_116_add_alias_rewards_2(self):
        card = TestCards.gift_card_2_manual()

        response = card.add_alias('9725550100').execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_117_remove_alias_rewards_1(self):
        card = TestCards.gift_card_1_swipe()

        response = card.remove_alias('9725550100').execute('retail')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_999_close_batch(self):
        try:
            response = BatchService.close_batch('retail')
            self.assertNotEqual(None, response)
        except Exception as e:
            if str(e.message).find(self.BATCH_NOT_OPEN) != -1 or str(
                    e.message).find(self.BATCH_EMPTY) != -1:
                return
