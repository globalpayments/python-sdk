"""
Test Recurring
"""

from datetime import datetime
import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities import Address, Customer, RecurringPaymentMethod
from globalpayments.api.entities.enums import (
    AddressType,
    RecurringSequence,
    RecurringType,
)
from globalpayments.api.entities.exceptions import (
    GatewayException,
    UnsupportedTransactionException,
)
from globalpayments.api.payment_methods import CreditCardData


class IntegrationGatewaysRealexConnectorRecurringTests(unittest.TestCase):
    """
    Ensure Recurring transactions works
    """

    config = PorticoConfig()
    config.merchant_id = "heartlandgpsandbox"
    config.account_id = "api"
    config.shared_secret = "secret"
    config.rebate_password = "rebate"
    config.refund_password = "refund"
    config.service_url = "https://api.sandbox.realexpayments.com/epage-remote.cgi"

    ServicesContainer.configure(config, "realex")

    card = CreditCardData()
    card.number = "4263970000005262"
    card.exp_month = "05"
    card.exp_year = "2019"
    card.cvn = "123"
    card.card_holder_name = "James Mason"

    new_customer = Customer()
    new_customer.key = "{}-Realex".format(datetime.now().strftime("%Y%m%d"))
    new_customer.title = "Mr."
    new_customer.first_name = "James"
    new_customer.last_name = "Mason"
    new_customer.company = "Realex Payments"
    new_customer.address = Address()
    new_customer.address.street_address_1 = "Flat 123"
    new_customer.address.street_address_2 = "House 456"
    new_customer.address.street_address_3 = "The Cul-De-Sac"
    new_customer.address.city = "Halifax"
    new_customer.address.province = "West Yorkshire"
    new_customer.address.postal_code = "W6 9HR"
    new_customer.address.country = "United Kingdom"
    new_customer.home_phone = "+35312345678"
    new_customer.work_phone = "+3531987654321"
    new_customer.fax = "+24546871258"
    new_customer.mobile_phone = "+25544778544"
    new_customer.email = "test@example.com"
    new_customer.comments = "Campaign Ref E7373G"

    def customer_id(self):
        return "{}-Realex".format(datetime.now().strftime("%Y%m%d"))

    def payment_id(self, t):
        return "{}-Realex-{}".format(datetime.now().strftime("%Y%m%d"), t)

    def test_001a_create_customer(self):
        try:
            customer = self.new_customer.create("realex")
            self.assertNotEqual(None, customer)
        except GatewayException as exc:
            if int(exc.response_code) != 501:
                raise exc

    def test_001b_create_payment_method(self):
        try:
            payment_method = self.new_customer.add_payment_method(
                self.payment_id("credit"), self.card
            ).create("realex")
            self.assertNotEqual(None, payment_method)
        except GatewayException as exc:
            if int(exc.response_code) != 520:
                raise exc

    def test_002a_edit_customer(self):
        customer = Customer()
        customer.key = self.customer_id()
        customer.first_name = "Perry"
        customer.save_changes("realex")

    def test_002b_edit_payment_method(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )
        payment_method.payment_method = CreditCardData()
        payment_method.payment_method.number = "5425230000004415"
        payment_method.payment_method.exp_month = "10"
        payment_method.payment_method.exp_year = "2020"
        payment_method.payment_method.card_holder_name = "Philip Marlowe"
        payment_method.save_changes("realex")

    def test_002c_edit_payment_method_exp_date_only(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )
        payment_method.payment_method = CreditCardData()
        payment_method.payment_method.card_type = "MC"
        payment_method.payment_method.exp_month = "10"
        payment_method.payment_method.exp_year = "2020"
        payment_method.payment_method.card_holder_name = "Philip Marlowe"
        payment_method.save_changes("realex")

    def test_003_find_customer_throws_exception(self):
        with self.assertRaises(UnsupportedTransactionException):
            Customer.find(self.customer_id(), "realex")

    def test_004a_charge_stored_card(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )

        response = (
            payment_method.charge(10)
            .with_currency("USD")
            .with_cvn("123")
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_004b_verify_stored_card(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )

        response = payment_method.verify().with_cvn("123").execute("realex")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_004c_refund_stored_card(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )

        response = payment_method.refund(10.01).with_currency("USD").execute("realex")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_005_recurring_payment(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )

        response = (
            payment_method.charge(12)
            .with_currency("USD")
            .with_recurring_info(RecurringType.Fixed, RecurringSequence.First)
            .execute("realex")
        )

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code, response.response_message)

    def test_006_delete_payment_method(self):
        payment_method = RecurringPaymentMethod(
            self.customer_id(), self.payment_id("Credit")
        )
        payment_method.delete(config_name="realex")
