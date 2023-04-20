'''
Test Token Management
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.payment_methods import CreditCardData


class IntegrationGatewaysPorticoConnectorTokenManageTests(unittest.TestCase):
    '''
    Ensure token management requests work
    '''

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MZ97AQBP-EgA5j5Um2fXMdCqcukek6pG6VmVjDg02A'
    config.service_url = 'https://cert.api2.heartlandportico.com'
    config.developer_id = '000000'
    config.version_number = '0000'

    ServicesContainer.configure(config)

    card = CreditCardData()
    card.number = '4111111111111111'
    card.exp_month = '12'
    card.exp_year = '2025'
    card.cvn = '123'

    def test_token_update_expiry(self):
        response = self.card.authorize(14) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .with_request_multi_use_token(True) \
            .execute()

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)
        self.assertNotEqual(None, response.token)

        self.card.exp_year = '2028'
        self.card.exp_month = '10'
        self.card.token = response.token

        update_response = self.card.update_token_expiry()
        self.assertEqual(True, update_response)

    def test_delete_token(self):
        self.card.token = None

        response = self.card.authorize(14) \
            .with_currency('USD') \
            .with_allow_duplicates(True) \
            .with_request_multi_use_token(True) \
            .execute()

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)
        self.assertNotEqual(None, response.token)
        self.card.token = response.token

        delete_response = self.card.delete_token()
        self.assertEqual(True, delete_response)
