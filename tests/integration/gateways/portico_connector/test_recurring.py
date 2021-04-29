'''
Test Check
'''

import unittest, datetime
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.entities import Address, Transaction, Customer, RecurringPaymentMethod, Schedule
from globalpayments.api.entities.enums import AccountType, CheckType, EntryMethod, PaymentMethodType, SecCode
from globalpayments.api.payment_methods import ECheck
from globalpayments.api.services import ReportingService

class IntegrationGatewaysPorticoConnectorACHTests(unittest.TestCase):
    '''
    Ensure PayPlan functionality works
    '''

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MXvdAQB61V4AkyM-x3EJuY6hkEaCzaMimTWav7mVfQ'
    config.service_url = 'https://cert.api2.heartlandportico.com'
    config.developer_id = '000000'
    config.version_number = '0000'
    ServicesContainer.configure(config)

    test_02a_trans_id = None

    def simple_timestamp():
        now = datetime.datetime.now()
        return now.strftime("%H%M%S")

    time_stamp = simple_timestamp()
    customer_id = "Customer_" + simple_timestamp()
    ACH_id = "ACH_" + simple_timestamp()
    schedule_id = "Schedule_" + simple_timestamp()

    address = Address()
    address.street_address_1 = '1 Heartland Way'
    address.city = 'Jeffersonville'
    address.province = 'IN'
    address.postal_code = '47130'
    address.country = "USA"

    # Using Heartland ACH as the check processor (not Sage/Paya)
    check = ECheck()
    check.account_number = '1357902468'
    check.routing_number = '122000030'
    check.check_type = CheckType.Personal
    check.sec_code = SecCode.PPD
    check.account_type = AccountType.Checking
    check.entry_mode = EntryMethod.Manual
    check.check_holder_name = 'Tony Smedal'

    def test_01_create_customer(self):
        new_customer = Customer()
        new_customer.id = self.customer_id
        new_customer.title = "Mr"
        new_customer.first_name = "Tony"
        new_customer.last_name = "Smedal"
        new_customer.company = "Global Payments"
        new_customer.address = self.address
        new_customer.home_phone = "5556667777"
        new_customer.email = "developers@globalpayments.com"
        new_customer.create()

        self.assertIsNotNone(Customer.find(self.customer_id))

    def test_02_create_ACH_payment_method(self):
        found_customer = Customer.find(self.customer_id)
        found_customer.add_payment_method(self.ACH_id, self.check).create()

        self.assertIsNotNone(RecurringPaymentMethod.find(self.ACH_id))

    def test_02a_charge_that_payment_method(self):
        found_payment_method = RecurringPaymentMethod.find(self.ACH_id)
        found_payment_method.sec_code = SecCode.WEB

        charge_result = found_payment_method.charge(10.99)\
            .with_currency("USD")\
            .with_one_time_payment(True)\
            .execute()

        self.assertIsNotNone(charge_result.transaction_id)
        self.assertEqual(charge_result.response_code, "00")

        self.__class__.test_02a_trans_id = charge_result.transaction_id

    def test_02b_void_test_02a(self):
        refund_response = Transaction.from_id(self.test_02a_trans_id, PaymentMethodType.ACH)\
            .void()\
            .execute()

        self.assertEqual(refund_response.response_code, "00")
        self.assertIsNotNone(refund_response.transaction_id)
        self.assertEqual(
            ReportingService.transaction_detail(self.test_02a_trans_id).execute().status,
            "V"
        )
            
    def test_03_create_payment_schedule(self):
        found_payment_method = RecurringPaymentMethod.find(self.ACH_id)
        found_payment_method.add_schedule(self.schedule_id)\
            .with_status('Active')\
            .with_amount(12.34)\
            .with_currency('USD')\
            .with_start_date(datetime.date(2022, 1, 1))\
            .with_frequency('Weekly')\
            .with_reprocessing_count(2)\
            .with_email_receipt('All')\
            .create()

        self.assertIsNotNone(Schedule.find(self.schedule_id))
