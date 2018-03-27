'''
Test Check
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities import Address, Transaction
from globalpayments.api.entities.enums import AccountType, CheckType, EntryMethod, PaymentMethodType, SecCode
from globalpayments.api.payment_methods import ECheck


class IntegrationGatewaysPorticoConnectorCertificationACHTests(
        unittest.TestCase):
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

    def check(self, sec_code, check_type, account_type, check_name=None):
        check = ECheck()
        check.account_number = '24413815'
        check.routing_number = '490000018'
        check.check_type = check_type
        check.sec_code = sec_code
        check.account_type = account_type
        check.entry_mode = EntryMethod.Manual
        check.check_holder_name = 'John Doe'
        check.drivers_license_number = '09876543210'
        check.drivers_license_state = 'TX'
        check.phone_number = '8003214567'
        check.birth_year = '1997'
        check.ssn_last_4 = '4321'
        if check_name:
            check.check_name = check_name
        return check

    # ACH Debit - Consumer

    def test_001_consumer_personal_checking(self):
        check = self.check(SecCode.PPD, CheckType.Personal,
                           AccountType.Checking)

        response = check.charge(11.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 25
        void_response = response.void().execute('ach')

        self.assertNotEqual(None, void_response)
        self.assertEqual('00', void_response.response_code,
                         void_response.response_message)

    def test_002_consumer_business_checking(self):
        check = self.check(SecCode.PPD, CheckType.Business,
                           AccountType.Checking)

        response = check.charge(12.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_003_consumer_personal_savings(self):
        check = self.check(SecCode.PPD, CheckType.Personal,
                           AccountType.Savings)

        response = check.charge(13.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_004_consumer_business_savings(self):
        check = self.check(SecCode.PPD, CheckType.Business,
                           AccountType.Savings)

        response = check.charge(14.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # ACH Debit - Corporate

    def test_005_corporate_personal_checking(self):
        check = self.check(SecCode.CCD, CheckType.Personal,
                           AccountType.Checking, 'Heartland Pays')

        response = check.charge(15.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

        # test case 26
        void_response = response.void().execute('ach')

        self.assertNotEqual(None, void_response)
        self.assertEqual('00', void_response.response_code,
                         void_response.response_message)

    def test_006_corporate_business_checking(self):
        check = self.check(SecCode.CCD, CheckType.Business,
                           AccountType.Checking, 'Heartland Pays')

        response = check.charge(16.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_007_corporate_personal_savings(self):
        check = self.check(SecCode.CCD, CheckType.Personal,
                           AccountType.Savings, 'Heartland Pays')

        response = check.charge(17.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_008_corporate_business_savings(self):
        check = self.check(SecCode.CCD, CheckType.Business,
                           AccountType.Savings, 'Heartland Pays')

        response = check.charge(18.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # ACH Debit - eGold

    def test_009_egold_personal_checking(self):
        check = self.check(SecCode.POP, CheckType.Personal,
                           AccountType.Checking)

        response = check.charge(11.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_010_egold_business_checking(self):
        check = self.check(SecCode.POP, CheckType.Business,
                           AccountType.Checking)

        response = check.charge(12.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_011_egold_personal_savings(self):
        check = self.check(SecCode.POP, CheckType.Personal,
                           AccountType.Savings)

        response = check.charge(13.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_012_egold_business_savings(self):
        check = self.check(SecCode.POP, CheckType.Business,
                           AccountType.Savings)

        response = check.charge(14.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # ACH Debit - eSilver

    def test_013_esilver_personal_checking(self):
        check = self.check(SecCode.POP, CheckType.Personal,
                           AccountType.Checking)

        response = check.charge(15.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_014_esilver_business_checking(self):
        check = self.check(SecCode.POP, CheckType.Business,
                           AccountType.Checking)

        response = check.charge(16.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_015_esilver_personal_savings(self):
        check = self.check(SecCode.POP, CheckType.Personal,
                           AccountType.Savings)

        response = check.charge(17.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_016_esilver_business_savings(self):
        check = self.check(SecCode.POP, CheckType.Business,
                           AccountType.Savings)

        response = check.charge(18.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # ACH Debit - eBronze

    @unittest.skip('eBronze support cannot be configured with the others')
    def test_017_ebronze_personal_checking(self):
        check = self.check(SecCode.EBronze, CheckType.Personal,
                           AccountType.Checking)

        response = check.charge(19.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    @unittest.skip('eBronze support cannot be configured with the others')
    def test_018_ebronze_business_checking(self):
        check = self.check(SecCode.EBronze, CheckType.Business,
                           AccountType.Checking)

        response = check.charge(20.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    @unittest.skip('eBronze support cannot be configured with the others')
    def test_019_ebronze_personal_savings(self):
        check = self.check(SecCode.EBronze, CheckType.Personal,
                           AccountType.Savings)

        response = check.charge(21.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    @unittest.skip('eBronze support cannot be configured with the others')
    def test_020_ebronze_business_savings(self):
        check = self.check(SecCode.EBronze, CheckType.Business,
                           AccountType.Savings)

        response = check.charge(22.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    # ACH Debit - WEB

    def test_021_web_personal_checking(self):
        check = self.check(SecCode.WEB, CheckType.Personal,
                           AccountType.Checking)

        response = check.charge(23.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_022_web_business_checking(self):
        check = self.check(SecCode.WEB, CheckType.Business,
                           AccountType.Checking)

        response = check.charge(24.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_023_web_personal_savings(self):
        check = self.check(SecCode.WEB, CheckType.Personal,
                           AccountType.Savings)

        response = check.charge(25.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)

    def test_024_web_business_savings(self):
        check = self.check(SecCode.WEB, CheckType.Business,
                           AccountType.Savings)

        response = check.charge(5.00) \
            .with_currency('USD') \
            .with_address(self.address) \
            .with_allow_duplicates(True) \
            .execute('ach')

        self.assertNotEqual(None, response)
        self.assertEqual('00', response.response_code,
                         response.response_message)
