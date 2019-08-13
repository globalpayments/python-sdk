'''
Test EBT
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities import EncryptionData, Transaction
from globalpayments.api.entities.enums import PaymentMethodType
from globalpayments.api.entities.exceptions import UnsupportedTransactionException
from globalpayments.api.payment_methods import EBTCardData, EBTTrackData


class IntegrationGatewaysPorticoConnectorEbtTests(unittest.TestCase):
    '''
    Ensure EBT transactions work
    '''

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MaePAQBr-1QAqjfckFC8FTbRTT120bVQUlfVOjgCBw'
    config.service_url = 'https://cert.api2.heartlandportico.com'
    config.developer_id = '000000'
    config.version_number = '0000'

    ServicesContainer.configure(config, 'ebt')

    card = EBTCardData()
    card.number = '4012002000060016'
    card.exp_month = '12'
    card.exp_year = '2025'
    card.cvn = '123'
    card.pin_block = '32539F50C245A6A93D123412324000AA'

    track = EBTTrackData()
    track.value = '<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|LO04K0WFOmdkDz0um+GwUkILL8ZZOP6Zc4rCpZ9+kg2T3JBT4AEOilWTI|+++++++Dbbn04ekG|11;4012001000000016=25120000000000000000?|1u2F/aEhbdoPixyAPGyIDv3gBfF|+++++++Dbbn04ekG|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>'
    track.pin_block = '32539F50C245A6A93D123412324000AA'
    track.encryption_data = EncryptionData()
    track.encryption_data.version = '01'

    def test_ebt_balance_inquiry(self):
        response = self.card.balance_inquiry().execute()

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_ebt_sale(self):
        response = self.card.charge(17.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('ebt')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_ebt_refund(self):
        response = self.card.refund(16.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('ebt')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_ebt_track_balance_inquiry(self):
        response = self.track.balance_inquiry().execute()

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_ebt_track_sale(self):
        response = self.track.charge(17.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('ebt')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_ebt_track_refund(self):
        response = self.track.refund(16.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('ebt')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_ebt_cannot_refund_from_transaction_id_only(self):
        with self.assertRaises(UnsupportedTransactionException):
            Transaction.from_id("1234567890", PaymentMethodType.EBT) \
                .refund() \
                .with_currency('USD') \
                .execute('ebt')
