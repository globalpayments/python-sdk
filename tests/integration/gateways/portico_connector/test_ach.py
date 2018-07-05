'''
Test Check
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities import Address, Transaction
from globalpayments.api.entities.enums import AccountType, CheckType, EntryMethod, PaymentMethodType, SecCode
from globalpayments.api.payment_methods import ECheck


class IntegrationGatewaysPorticoConnectorACHTests(unittest.TestCase):
    '''
    Ensure check transactions work
    '''

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A'
    config.service_url = 'https://cert.api2.heartlandportico.com'

    ServicesContainer.configure(config, 'ach')

    address = Address()
    address.street_address_1 = '123 Main St.'
    address.city = 'Downtown'
    address.province = 'NJ'
    address.postal_code = '12345'

    check = ECheck()
    check.account_number = '24413815'
    check.routing_number = '490000018'
    check.check_type = CheckType.Personal
    check.sec_code = SecCode.PPD
    check.account_type = AccountType.Checking
    check.entry_mode = EntryMethod.Manual
    check.check_holder_name = 'John Doe'
    check.drivers_license_number = '09876543210'
    check.drivers_license_state = 'TX'
    check.phone_number = '8003214567'
    check.birth_year = '1997'
    check.ssn_last_4 = '4321'

    def test_check_sale(self):
        response = self.check.charge(11) \
            .with_currency('USD') \
            .with_address(self.address) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

    def test_check_void_from_transaction_id(self):
        response = self.check.charge(10) \
            .with_currency('USD') \
            .with_address(self.address) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code)

        void_response = Transaction.from_id(response.transaction_id, PaymentMethodType.ACH) \
            .void() \
            .execute('ach')

        self.assertNotEqual(None, void_response)
        self.assertEqual('00', void_response.response_code)

    def test_check_crypto_gold_standard(self):
        gold_config = ServicesConfig()
        gold_config.secret_api_key = 'skapi_cert_MTyMAQBiHVEAewvIzXVFcmUd2UcyBge_eCpaASUp0A'
        gold_config.service_url = 'https://cert.api2-c.heartlandportico.com'

        ServicesContainer.configure(gold_config, 'gold standard')

        response = self.check.charge(10)\
            .with_currency('USD')\
            .with_address(self.address)\
            .with_allow_duplicates(True)\
            .execute('gold standard')
        self.assertNotEqual(None, response);
        self.assertEqual('00', response.response_code)
