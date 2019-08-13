'''
Test Debit
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities import EncryptionData, Transaction
from globalpayments.api.entities.enums import PaymentMethodType
from globalpayments.api.entities.exceptions import UnsupportedTransactionException
from globalpayments.api.payment_methods import DebitTrackData


class IntegrationGatewaysPorticoConnectorDebitTests(unittest.TestCase):
    '''
    Ensure debit transactions work
    '''

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MaePAQBr-1QAqjfckFC8FTbRTT120bVQUlfVOjgCBw'
    config.service_url = 'https://cert.api2.heartlandportico.com'
    config.developer_id = '000000'
    config.version_number = '0000'

    ServicesContainer.configure(config, 'debit')

    track = DebitTrackData()
    track.value = '<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|LO04K0WFOmdkDz0um+GwUkILL8ZZOP6Zc4rCpZ9+kg2T3JBT4AEOilWTI|+++++++Dbbn04ekG|11;4012001000000016=25120000000000000000?|1u2F/aEhbdoPixyAPGyIDv3gBfF|+++++++Dbbn04ekG|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>'
    track.pin_block = '32539F50C245A6A93D123412324000AA'
    track.encryption_data = EncryptionData()
    track.encryption_data.version = '01'

    def test_debit_sale(self):
        response = self.track.charge(17.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('debit')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    @unittest.skip('Expected failure')
    def test_debit_add_value(self):
        response = self.track.add_value(15.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('debit')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_debit_refund(self):
        response = self.track.refund(16.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('debit')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_debit_reverse(self):
        response = self.track.reverse(17.01) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .execute('debit')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_debit_cannot_refund_from_transaction_id_only(self):
        with self.assertRaises(UnsupportedTransactionException):
            Transaction.from_id("1234567890", PaymentMethodType.Debit) \
                .refund() \
                .with_currency('USD') \
                .execute('debit')

    def test_debit_cannot_reverse_from_transaction_id_only(self):
        with self.assertRaises(UnsupportedTransactionException):
            Transaction.from_id("1234567890", PaymentMethodType.Debit) \
                .reverse() \
                .with_currency('USD') \
                .execute('debit')

    def test_check_crypto_gold_standard(self):
        gold_config = ServicesConfig()
        gold_config.secret_api_key = 'skapi_cert_MaePAQBr-1QAqjfckFC8FTbRTT120bVQUlfVOjgCBw'
        gold_config.service_url = 'https://cert.api2-c.heartlandportico.com'

        ServicesContainer.configure(gold_config, 'gold standard')
        response = self.track.charge(10)\
            .with_currency('USD')\
            .with_allow_duplicates(True)\
            .execute('gold standard')
        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)
