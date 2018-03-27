'''
Test builder validations
'''

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities.exceptions import BuilderException
from globalpayments.api.payment_methods import CreditCardData


class AuthorizationBuilderValidationTests(unittest.TestCase):
    '''
    Ensure AuthorizationBuilder validations work
    '''

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MTeSAQAfG1UA9qQDrzl-kz4toXvARyieptFwSKP24w'
    config.service_url = 'https://cert.api2.heartlandportico.com'

    ServicesContainer.configure(config)

    card = CreditCardData()
    card.number = '4111111111111111'
    card.exp_month = '12'
    card.exp_year = '2025'
    card.cvn = '123'
    card.card_holder_name = 'Joe Smith'

    def test_credit_auth_no_amount(self):
        with self.assertRaises(BuilderException):
            self.card.authorize().execute()

    def test_credit_auth_no_currency(self):
        with self.assertRaises(BuilderException):
            self.card.authorize(14).execute()

    def test_credit_auth_no_payment_method(self):
        with self.assertRaises(BuilderException):
            self.card.authorize(14) \
                .with_currency('USD') \
                .with_payment_method(None) \
                .execute()

    def test_credit_auth_no_validation_error(self):
        try:
            self.card.authorize(14) \
                .with_currency('USD') \
                .with_allow_duplicates(True) \
                .execute()
        except BuilderException:
            self.fail(
                'Properly configured auth builder should not raise exception')

    def test_credit_sale_no_amount(self):
        with self.assertRaises(BuilderException):
            self.card.charge().execute()

    def test_credit_sale_no_currency(self):
        with self.assertRaises(BuilderException):
            self.card.charge(14).execute()

    def test_credit_sale_no_payment_method(self):
        with self.assertRaises(BuilderException):
            self.card.charge(14) \
                .with_currency('USD') \
                .with_payment_method(None) \
                .execute()

    def test_credit_offline_no_amount(self):
        with self.assertRaises(BuilderException):
            self.card.authorize() \
                .with_offline_auth_code('12345') \
                .execute()

    def test_credit_offline_no_currency(self):
        with self.assertRaises(BuilderException):
            self.card.authorize(14) \
                .with_offline_auth_code('12345') \
                .execute()

    def test_credit_offline_no_auth_code(self):
        with self.assertRaises(BuilderException):
            self.card.authorize(14) \
                .with_currency('USD') \
                .with_offline_auth_code(None) \
                .execute()
