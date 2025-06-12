import unittest
from datetime import datetime

from globalpayments.api import ServicesContainer
from globalpayments.api.entities import Address, Customer
from globalpayments.api.entities import Transaction
from globalpayments.api.entities.enums import (
    CardChannel,
    StoredCredentialInitiator,
    StoredCredentialType,
    StoredCredentialSequence,
    StoredCredentialReason,
    PaymentMethodUsageMode,
)
from globalpayments.api.entities.exceptions import GatewayException
from globalpayments.api.entities.stored_credentials import StoredCredential
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.payment_methods import CreditCardData
from globalpayments.api.utils import GenerationUtils
from tests.data.GpApi_test_config import GpApiTestConfig


class IntegrationGatewaysGpApiConnectorCreditCardNotPresentTests(unittest.TestCase):
    """
    Ensure credit transactions work with GpApi
    """

    config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_NOT_PRESENT)
    ServicesContainer.configure(config)

    # Setup test data
    currency = "USD"

    # Setup card data
    date = datetime.now()
    card = CreditCardData()
    card.number = "4263970000005262"
    card.exp_month = str(date.month).zfill(2)
    card.exp_year = str(date.year + 1)
    card.cvn = "131"
    card.card_holder_name = "James Mason"

    def setUp(self):
        # Reset configuration before each test
        ServicesContainer.configure(self.config)

    def test_credit_sale(self):
        # Create address
        address = Address()
        address.street_address1 = "123 Main St."
        address.city = "Dallas"
        address.state = "TX"
        address.postal_code = "98765"
        address.country = "USA"

        # Execute transaction
        response = (
            self.card.charge(69)
            .with_currency(self.currency)
            .with_address(address)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)
        self.assertEqual(None, response.payer_details)

    def test_credit_sale_with_fingerprint(self):
        # Create address
        address = Address()
        address.street_address1 = "123 Main St."
        address.city = "Dallas"
        address.state = "TX"
        address.postal_code = "98765"
        address.country = "USA"

        # Create customer with fingerprint
        customer = Customer()
        customer.device_fingerprint = "ALWAYS"

        # Execute transaction
        response = (
            self.card.charge(69)
            .with_currency(self.currency)
            .with_address(address)
            .with_customer_data(customer)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)
        self.assertNotEqual(None, response.fingerprint)
        self.assertNotEqual(None, response.fingerprint_indicator)

    def test_credit_sale_with_fingerprint_success(self):
        # Create customer with fingerprint
        customer = Customer()
        customer.device_fingerprint = "ON_SUCCESS"

        # Execute transaction
        response = (
            self.card.charge(69)
            .with_currency(self.currency)
            .with_customer_data(customer)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)
        self.assertNotEqual(None, response.fingerprint)
        self.assertNotEqual(None, response.fingerprint_indicator)

    def test_credit_authorization(self):
        # Execute authorization
        response = (
            self.card.authorize(42)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, response.response_message)
        self.assertEqual(None, response.payer_details)

    def test_credit_authorization_then_capture(self):
        # Execute authorization
        transaction = (
            self.card.authorize(42)
            .with_currency(self.currency)
            .with_order_id("123456-78910")
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)

        # Execute capture
        capture = transaction.capture(30).with_gratuity(12).execute()

        # Validate capture response
        self.assertNotEqual(None, capture)
        self.assertEqual("SUCCESS", capture.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture.response_message)

    def test_credit_authorization_then_capture_with_fingerprint(self):
        # Create customer with fingerprint
        customer = Customer()
        customer.device_fingerprint = "ON_SUCCESS"

        # Execute authorization
        transaction = (
            self.card.authorize(42)
            .with_currency(self.currency)
            .with_order_id("123456-78910")
            .with_allow_duplicates(True)
            .with_customer_data(customer)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)
        self.assertNotEqual(None, transaction.fingerprint)
        self.assertNotEqual(None, transaction.fingerprint_indicator)

        # Execute capture
        capture = transaction.capture(30).with_gratuity(12).execute()

        # Validate capture response
        self.assertNotEqual(None, capture)
        self.assertEqual("SUCCESS", capture.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture.response_message)

    def test_credit_authorization_then_capture_with_idempotency(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Execute authorization
        transaction = (
            self.card.authorize(42)
            .with_currency(self.currency)
            .with_idempotency_key(idempotency_key)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)

        # Try to execute capture with same idempotency key (should fail)
        try:
            transaction.capture(30).with_idempotency_key(idempotency_key).with_gratuity(
                12
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_credit_authorization_for_multicapture(self):
        # Execute authorization with multi-capture
        transaction = (
            self.card.authorize(42)
            .with_currency("EUR")
            .with_multi_capture(True)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)
        self.assertTrue(transaction.multi_capture)

        # First capture
        capture = transaction.capture(10).execute()
        self.assertNotEqual(None, capture)
        self.assertEqual("SUCCESS", capture.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture.response_message)

        # Second capture
        capture2 = transaction.capture(10).execute()
        self.assertNotEqual(None, capture2)
        self.assertEqual("SUCCESS", capture2.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture2.response_message)

        # Third capture
        capture3 = transaction.capture(10).execute()
        self.assertNotEqual(None, capture3)
        self.assertEqual("SUCCESS", capture3.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture3.response_message)

    def test_credit_charge_with_same_idempotency_key(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Execute charge transaction
        transaction = (
            self.card.charge(69)
            .with_currency("EUR")
            .with_idempotency_key(idempotency_key)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Try to execute another charge with same idempotency key (should fail)
        try:
            self.card.charge(69).with_currency("EUR").with_idempotency_key(
                idempotency_key
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertTrue(transaction.transaction_id in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_credit_refund(self):
        # Execute transaction
        response = (
            self.card.refund(16)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )
        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)

    def test_credit_refund_with_fingerprint(self):
        # Create customer with fingerprint
        customer = Customer()
        customer.device_fingerprint = "ON_SUCCESS"
        # Execute transaction
        response = (
            self.card.refund(16)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .with_customer_data(customer)
            .execute()
        )
        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)
        self.assertNotEqual(None, response.fingerprint)
        self.assertNotEqual(None, response.fingerprint_indicator)

    def test_credit_default_refund_with_idempotency_key(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()
        # Execute charge transaction
        transaction = (
            self.card.charge(50)
            .with_currency(self.currency)
            .with_idempotency_key(idempotency_key)
            .with_allow_duplicates(True)
            .execute()
        )
        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Try to execute refund with same idempotency key (should fail)
        try:
            transaction.refund(50).with_currency(self.currency).with_idempotency_key(
                idempotency_key
            ).with_allow_duplicates(True).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_credit_sale_tokenized_with_stored_credential(self):
        # Create stored credentials
        stored_credentials = StoredCredential()
        stored_credentials.initiator = StoredCredentialInitiator.Merchant
        stored_credentials.type = StoredCredentialType.INSTALLMENT
        stored_credentials.sequence = StoredCredentialSequence.SUBSEQUENT
        stored_credentials.reason = StoredCredentialReason.INCREMENTAL

        # Tokenize card
        tokenize_response = self.card.tokenize().execute()
        token_id = tokenize_response.token

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        tokenized_card.card_holder_name = "James Mason"

        # Execute charge with stored credentials
        response = (
            tokenized_card.charge(50)
            .with_currency("EUR")
            .with_stored_credential(stored_credentials)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)

    def test_credit_sale_with_stored_credential(self):
        # Create stored credentials
        stored_credentials = StoredCredential()
        stored_credentials.initiator = StoredCredentialInitiator.Merchant
        stored_credentials.type = StoredCredentialType.INSTALLMENT
        stored_credentials.sequence = StoredCredentialSequence.SUBSEQUENT
        stored_credentials.reason = StoredCredentialReason.INCREMENTAL

        # Execute charge with stored credentials
        response = (
            self.card.charge(50)
            .with_currency("EUR")
            .with_stored_credential(stored_credentials)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)

    def test_credit_sale_with_dynamic_descriptor(self):
        # Set dynamic descriptor
        dynamic_descriptor = "My company"

        # Execute charge with dynamic descriptor
        response = (
            self.card.charge(50)
            .with_currency("EUR")
            .with_dynamic_descriptor(dynamic_descriptor)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)

    def test_credit_reverse_with_wrong_id(self):
        # Create transaction with random ID
        transaction = Transaction()
        transaction.transaction_id = GenerationUtils.get_uuid()

        # Try to reverse transaction (should fail)
        try:
            transaction.reverse().with_currency(self.currency).with_allow_duplicates(
                True
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40008", error.response_code)
            self.assertTrue("RESOURCE_NOT_FOUND" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_credit_verify(self):
        # Execute verification
        response = self.card.verify().with_currency(self.currency).execute()

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("VERIFIED", response.response_message)

    def test_credit_verification_with_stored_credential(self):
        # Create stored credentials
        stored_credentials = StoredCredential()
        stored_credentials.initiator = StoredCredentialInitiator.Merchant
        stored_credentials.type = StoredCredentialType.INSTALLMENT
        stored_credentials.sequence = StoredCredentialSequence.SUBSEQUENT
        stored_credentials.reason = StoredCredentialReason.INCREMENTAL

        # Execute verification with stored credentials
        response = (
            self.card.verify()
            .with_currency(self.currency)
            .with_stored_credential(stored_credentials)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("VERIFIED", response.response_message)

    def test_credit_verification_with_idempotency_key(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Execute verification with idempotency key
        response = (
            self.card.verify()
            .with_currency(self.currency)
            .with_idempotency_key(idempotency_key)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("VERIFIED", response.response_message)

        # Try to execute another verification with same idempotency key (should fail)
        try:
            self.card.verify().with_currency(self.currency).with_idempotency_key(
                idempotency_key
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_credit_verification_with_address(self):
        # Create address
        address = Address()
        address.street_address1 = "123 Main St."
        address.city = "Downtown"
        address.state = "NJ"
        address.country = "US"
        address.postal_code = "12345"

        # Execute verification with address
        response = (
            self.card.verify()
            .with_currency(self.currency)
            .with_address(address)
            .execute()
        )

        # Validate response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("VERIFIED", response.response_message)

    def test_credit_verification_without_currency(self):
        # Try to verify without currency (should fail)
        try:
            self.card.verify().execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40005", error.response_code)
            self.assertTrue(
                "Request expects the following fields currency" in error.message
            )
            self.assertIsInstance(error, GatewayException)

    def test_credit_verification_invalid_cvv(self):
        # Create card with invalid CVV
        wrong_card = CreditCardData()
        wrong_card.number = "4263970000005262"
        wrong_card.exp_month = str(self.date.month).zfill(2)
        wrong_card.exp_year = str(self.date.year + 1)
        wrong_card.card_holder_name = "James Mason"
        wrong_card.cvn = "1234"  # Invalid CVV (too long)

        # Try to verify with invalid CVV (should fail)
        try:
            wrong_card.verify().with_currency(self.currency).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40085", error.response_code)
            self.assertTrue("Security Code/CVV2/CVC must be 3 digits" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_credit_verification_not_numeric_cvv(self):
        # Create card with non-numeric CVV
        wrong_card = CreditCardData()
        wrong_card.number = "4263970000005262"
        wrong_card.exp_month = str(self.date.month).zfill(2)
        wrong_card.exp_year = str(self.date.year + 1)
        wrong_card.card_holder_name = "James Mason"
        wrong_card.cvn = "SMA"  # Non-numeric CVV

        # Try to verify with non-numeric CVV (should fail)
        try:
            wrong_card.verify().with_currency(self.currency).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("50018", error.response_code)
            self.assertTrue("The line number 14 which contains" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_capture_higher_amount(self):
        # Execute authorization
        transaction = (
            self.card.authorize(55)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)

        # Capture higher amount (within 115% limit)
        capture = transaction.capture("60").execute()
        self.assertNotEqual(None, capture)
        self.assertEqual("SUCCESS", capture.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture.response_message)

        # Execute another authorization
        transaction2 = (
            self.card.authorize(30)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate second authorization response
        self.assertNotEqual(None, transaction2)
        self.assertEqual("SUCCESS", transaction2.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction2.response_message)

        # Try to capture amount over 115% limit (should fail)
        try:
            transaction2.capture("40").execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("50020", error.response_code)
            self.assertTrue(
                "Can't settle for more than 115% of that which you authorised"
                in error.message
            )
            self.assertIsInstance(error, GatewayException)

    def test_capture_lower_amount(self):
        # Execute authorization
        transaction = (
            self.card.authorize("55")
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)

        # Capture lower amount
        capture = transaction.capture("20").execute()
        self.assertNotEqual(None, capture)
        self.assertEqual("SUCCESS", capture.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture.response_message)

    def test_charge_then_refund_higher_amount(self):
        # Execute charge
        transaction = (
            self.card.charge(50)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Try to refund higher amount (should fail)
        try:
            transaction.refund(60).with_currency(self.currency).with_allow_duplicates(
                True
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40087", error.response_code)
            self.assertTrue(
                "You may only refund up to 115% of the original amount" in error.message
            )
            self.assertIsInstance(error, GatewayException)

    def test_capture_then_refund_higher_amount(self):
        # Execute authorization
        transaction = (
            self.card.authorize(55)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate authorization response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.PREAUTHORIZED, transaction.response_message)

        # Capture full amount
        capture = transaction.capture(55).execute()
        self.assertNotEqual(None, capture)
        self.assertEqual("SUCCESS", capture.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, capture.response_message)

        # Try to refund higher amount (should fail)
        try:
            transaction.refund(70).with_currency(self.currency).with_allow_duplicates(
                True
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40087", error.response_code)
            self.assertTrue(
                "You may only refund up to 115% of the original amount" in error.message
            )
            self.assertIsInstance(error, GatewayException)

    def test_verify_tokenized_payment_method_with_fingerprint(self):
        # Create customer with fingerprint
        customer = Customer()
        customer.device_fingerprint = "ALWAYS"

        # Tokenize card with fingerprint
        response = self.card.tokenize().with_customer_data(customer).execute()

        # Validate tokenization response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertNotEqual(None, response.fingerprint)

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = response.token

        # Verify tokenized card with fingerprint
        verify_response = (
            tokenized_card.verify()
            .with_currency(self.currency)
            .with_customer_data(customer)
            .execute()
        )

        # Validate verification response
        self.assertNotEqual(None, verify_response)
        self.assertEqual("SUCCESS", verify_response.response_code)
        self.assertEqual("VERIFIED", verify_response.response_message)
        self.assertNotEqual(None, verify_response.fingerprint)

    def test_verify_tokenized_payment_method_with_invalid_fingerprint(self):
        # Create customer with invalid fingerprint
        customer = Customer()
        customer.device_fingerprint = "NOT_ALWAYS"

        # Try to charge with invalid fingerprint (should fail)
        try:
            self.card.charge(60).with_currency(self.currency).with_customer_data(
                customer
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40213", error.response_code)
            self.assertTrue(
                "fingerprint_mode contains unexpected data" in error.message
            )
            self.assertIsInstance(error, GatewayException)

    def test_credit_sale_without_permissions(self):
        # Configure service with limited permissions
        config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_NOT_PRESENT)
        config.permissions = ["TRN_POST_Capture"]
        ServicesContainer.configure(config, "config_without_sale_permission")

        # Try to charge without permission (should fail)
        try:
            self.card.charge(50).with_currency(self.currency).with_allow_duplicates(
                True
            ).execute("config_without_sale_permission")
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40212", error.response_code)
            self.assertEqual(
                "Status Code: ACTION_NOT_AUTHORIZED - Permission not enabled to execute action",
                error.message,
            )
            self.assertIsInstance(error, GatewayException)

    def test_transaction_then_refund(self):
        # Execute charge
        transaction = (
            self.card.charge(50)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Execute partial refund
        partial_amount = "7.51"
        partial_refund = (
            transaction.refund(partial_amount).with_currency(self.currency).execute()
        )

        # Validate partial refund response
        self.assertNotEqual(None, partial_refund)
        self.assertEqual("SUCCESS", partial_refund.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, partial_refund.response_message)
        self.assertEqual(partial_amount, partial_refund.balance_amount)

        # Try to refund the rest (should fail because no amount specified)
        try:
            transaction.refund().with_currency(self.currency).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40087", error.response_code)
            self.assertTrue(
                "You may only refund up to 115% of the original amount" in error.message
            )
            self.assertIsInstance(error, GatewayException)

    def test_transaction_then_reversal(self):
        # Execute charge
        transaction = (
            self.card.charge(20)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Execute reversal with amount
        reverse = transaction.reverse(20).execute()

        # Validate reversal response
        self.assertNotEqual(None, reverse)
        self.assertEqual("SUCCESS", reverse.response_code)
        self.assertEqual(TransactionStatus.REVERSED, reverse.response_message)

    def test_transaction_then_default_reversal(self):
        # Execute charge
        transaction = (
            self.card.charge(20)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Execute default reversal (no amount specified)
        reverse = transaction.reverse().execute()

        # Validate reversal response
        self.assertNotEqual(None, reverse)
        self.assertEqual("SUCCESS", reverse.response_code)
        self.assertEqual(TransactionStatus.REVERSED, reverse.response_message)

    def test_transaction_then_reversal_with_idempotency_key(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Execute charge with idempotency key
        transaction = (
            self.card.charge(20)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .with_idempotency_key(idempotency_key)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Try to reverse with same idempotency key (should fail)
        try:
            transaction.reverse().with_idempotency_key(idempotency_key).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_transaction_then_partial_reversal(self):
        # Execute charge
        transaction = (
            self.card.charge(20)
            .with_currency(self.currency)
            .with_allow_duplicates(True)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

        # Try partial reversal (should fail)
        try:
            transaction.reverse(10).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40214", error.response_code)
            self.assertEqual(
                "Status Code: INVALID_REQUEST_DATA - partial reversal not supported",
                error.message,
            )
            self.assertIsInstance(error, GatewayException)

    def test_card_tokenization(self):
        # Tokenize card
        response = self.card.tokenize().execute()

        # Validate tokenization response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("ACTIVE", response.response_message)

    def test_card_tokenization_then_paying_with_token_single_to_multi_use(self):
        # Configure service with single-use token permission
        config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_NOT_PRESENT)
        config.permissions = ["PMT_POST_Create_Single"]
        ServicesContainer.configure(config, "single_use_token")

        # Tokenize card as single-use
        response = (
            self.card.tokenize(True)
            .with_payment_method_usage_mode(PaymentMethodUsageMode.SINGLE)
            .execute("single_use_token")
        )
        token_id = response.token

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        tokenized_card.card_holder_name = "James Mason"

        # Charge using single-use token and request multi-use token
        charge_response = (
            tokenized_card.charge(10)
            .with_currency("USD")
            .with_request_multi_use_token(True)
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, charge_response)
        self.assertEqual("SUCCESS", charge_response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, charge_response.response_message)
        self.assertTrue(charge_response.token.startswith("PMT_"))

        # Update tokenized card with new multi-use token
        tokenized_card.token = charge_response.token

        # Execute second charge with multi-use token
        second_charge_response = (
            tokenized_card.charge(10).with_currency("USD").execute()
        )

        # Validate second charge response
        self.assertNotEqual(None, second_charge_response)
        self.assertEqual("SUCCESS", second_charge_response.response_code)
        self.assertEqual(
            TransactionStatus.CAPTURED, second_charge_response.response_message
        )

    def test_card_tokenization_with_idempotency_key(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Tokenize card with idempotency key
        response = self.card.tokenize().with_idempotency_key(idempotency_key).execute()

        # Validate tokenization response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("ACTIVE", response.response_message)

        # Try to tokenize again with same idempotency key (should fail)
        try:
            self.card.tokenize().with_idempotency_key(idempotency_key).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_card_tokenization_then_paying_with_token(self):
        # Tokenize card
        response = self.card.tokenize().execute()
        token_id = response.token

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        tokenized_card.card_holder_name = "James Mason"

        # Charge using tokenized card
        charge_response = (
            tokenized_card.charge(69)
            .with_currency("EUR")
            .with_order_id("124214-214221")
            .execute()
        )

        # Validate charge response
        self.assertNotEqual(None, charge_response)
        self.assertEqual("SUCCESS", charge_response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, charge_response.response_message)

    def test_verify_tokenized_payment_method(self):
        # Tokenize card
        tokenize_response = self.card.tokenize().execute()

        # Validate tokenization response
        self.assertNotEqual(None, tokenize_response)
        self.assertEqual("SUCCESS", tokenize_response.response_code)
        self.assertEqual("ACTIVE", tokenize_response.response_message)

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = tokenize_response.token

        # Verify tokenized card
        response = tokenized_card.verify().with_currency(self.currency).execute()

        # Validate verification response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("VERIFIED", response.response_message)

    def test_verify_tokenized_payment_method_with_idempotency_key(self):
        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Tokenize card
        tokenize_response = self.card.tokenize().execute()

        # Validate tokenization response
        self.assertNotEqual(None, tokenize_response)
        self.assertEqual("SUCCESS", tokenize_response.response_code)
        self.assertEqual("ACTIVE", tokenize_response.response_message)

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = tokenize_response.token

        # Verify tokenized card with idempotency key
        response = (
            tokenized_card.verify()
            .with_currency(self.currency)
            .with_idempotency_key(idempotency_key)
            .execute()
        )

        # Validate verification response
        self.assertNotEqual(None, response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual("VERIFIED", response.response_message)

        # Try to verify again with same idempotency key (should fail)
        try:
            tokenized_card.verify().with_currency(self.currency).with_idempotency_key(
                idempotency_key
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_verify_tokenized_payment_method_with_wrong_id(self):
        # Create tokenized card with random token ID
        tokenized_card = CreditCardData()
        tokenized_card.token = f"PMT_{GenerationUtils.get_uuid()}"

        # Try to verify with wrong token ID (should fail)
        try:
            tokenized_card.verify().with_currency(self.currency).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40116", error.response_code)
            self.assertEqual(
                f"Status Code: RESOURCE_NOT_FOUND - payment_method {tokenized_card.token} not found at this location.",
                error.message,
            )
            self.assertIsInstance(error, GatewayException)

    def test_card_tokenization_then_update(self):
        # Tokenize card
        response = self.card.tokenize().execute()
        token_id = response.token

        # Create tokenized card with updated expiration
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        date = datetime.now()
        tokenized_card.exp_month = str(
            date.month + 2 if date.month <= 10 else (date.month + 2) % 12
        ).zfill(2)
        tokenized_card.exp_year = str(date.year + 2)

        # Update token expiry
        update_token_expiry_res = tokenized_card.update_token_expiry()

        # Validate update response
        self.assertNotEqual(None, update_token_expiry_res)

    def test_card_update_wrong_id(self):
        # Create tokenized card with random token ID
        tokenized_card = CreditCardData()
        tokenized_card.token = "PMT_" + GenerationUtils.get_uuid()
        date = datetime.now()
        tokenized_card.exp_month = str(
            date.month + 2 if date.month <= 10 else (date.month + 2) % 12
        ).zfill(2)
        tokenized_card.exp_year = str(date.year + 2)

        # Try to update token with wrong ID (should fail)
        try:
            tokenized_card.update_token_expiry()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual(
                f"Status Code: RESOURCE_NOT_FOUND - payment_method {tokenized_card.token} not found at this location.",
                error.message,
            )
            self.assertIsInstance(error, GatewayException)

    def test_card_tokenization_then_update_with_idempotency_key(self):
        # Tokenize card
        response = self.card.tokenize().execute()
        token_id = response.token

        # Create tokenized card with updated expiration
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        date = datetime.now()
        tokenized_card.exp_month = str(
            date.month + 2 if date.month <= 10 else (date.month + 2) % 12
        ).zfill(2)
        tokenized_card.exp_year = str(date.year + 2)

        # Generate idempotency key
        idempotency_key = GenerationUtils.get_uuid()

        # Update token with idempotency key
        update_token_expiry_res = (
            tokenized_card.update_token()
            .with_idempotency_key(idempotency_key)
            .execute()
        )

        # Validate update response
        self.assertNotEqual(None, update_token_expiry_res)
        self.assertEqual("SUCCESS", update_token_expiry_res.response_code)
        self.assertEqual("ACTIVE", update_token_expiry_res.response_message)

        # Try to update again with same idempotency key (should fail)
        try:
            tokenized_card.update_token().with_idempotency_key(
                idempotency_key
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40039", error.response_code)
            self.assertTrue("Idempotency Key seen before" in error.message)
            self.assertIsInstance(error, GatewayException)

        # Verify the updated token
        verify_response = (
            tokenized_card.verify()
            .with_currency(self.currency)
            .with_idempotency_key(idempotency_key)
            .execute()
        )

        # Validate verification response
        self.assertNotEqual(None, verify_response)
        self.assertEqual("SUCCESS", verify_response.response_code)
        self.assertEqual("VERIFIED", verify_response.response_message)

        # Update token again with new expiration
        tokenized_card.exp_year = str(date.year + 3)
        update_token_expiry_res2 = tokenized_card.update_token_expiry()

        # Validate second update response
        self.assertNotEqual(None, update_token_expiry_res2)

    def test_credit_refund_transaction_wrong_id(self):
        # Create transaction with random ID
        transaction = Transaction()
        transaction.transaction_id = GenerationUtils.get_uuid()

        # Try to refund with wrong transaction ID (should fail)
        try:
            transaction.refund(10).with_currency(self.currency).with_allow_duplicates(
                True
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertTrue("RESOURCE_NOT_FOUND" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_card_tokenization_missing_card_number(self):
        # Create card without number
        card = CreditCardData()

        # Try to tokenize without card number (should fail)
        try:
            card.tokenize().execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual(
                "Status Code: MANDATORY_DATA_MISSING - Request expects the following fields : number",
                error.message,
            )
            self.assertIsInstance(error, GatewayException)

    # def test_update_payment_token(self):
    #     # Set start date for search (30 days ago)
    #     start_date = datetime.now()
    #     start_date = start_date.replace(
    #         day=start_date.day - 30, hour=0, minute=0, second=0
    #     )
    #
    #     # Search for stored payment methods
    #     response = (
    #         ReportingService.find_stored_payment_methods_paged(1, 1)
    #         .order_by(StoredPaymentMethodSortProperty.TIME_CREATED, SortDirection.DESC)
    #         .where(
    #             SearchCriteria.START_DATE,
    #             f"{start_date.year}-{str(start_date.month).zfill(2)}-{str(start_date.day).zfill(2)}",
    #         )
    #         .execute()
    #     )
    #
    #     # Validate search response
    #     self.assertEqual(1, len(response.result))
    #
    #     pmt_token = response.result[0]
    #     self.assertNotEqual(None, pmt_token)
    #
    #     # Create tokenized card with updated info
    #     tokenized_card = CreditCardData()
    #     tokenized_card.token = pmt_token.payment_method_id
    #     date = datetime.now()
    #     tokenized_card.card_holder_name = "James BondUp"
    #     tokenized_card.exp_month = str(
    #         date.month + 2 if date.month <= 10 else (date.month + 2) % 12
    #     ).zfill(2)
    #     tokenized_card.exp_year = str(date.year + 4)
    #     tokenized_card.number = "4263970000005262"
    #
    #     # Update token
    #     response_update_token = (
    #         tokenized_card.update_token()
    #         .with_payment_method_usage_mode(PaymentMethodUsageMode.MULTIPLE)
    #         .execute()
    #     )
    #
    #     # Validate update response
    #     self.assertNotEqual(None, response_update_token)
    #     self.assertEqual("SUCCESS", response_update_token.response_code)
    #     self.assertEqual("ACTIVE", response_update_token.response_message)
    #     self.assertEqual(pmt_token.payment_method_id, response_update_token.token)
    #     self.assertEqual(
    #         PaymentMethodUsageMode.MULTIPLE, response_update_token.token_usage_mode
    #     )

    def test_card_tokenization_then_update_then_charge(self):
        # Configure service with single-use token permission
        config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_NOT_PRESENT)
        config.permissions = ["PMT_POST_Create_Single"]
        ServicesContainer.configure(config, "single_use_token")

        # Tokenize card as single-use
        response = (
            self.card.tokenize()
            .with_payment_method_usage_mode(PaymentMethodUsageMode.SINGLE)
            .execute("single_use_token")
        )

        token_id = response.token

        # Create tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        tokenized_card.card_holder_name = "GpApi"

        # Update token to multi-use
        response_update_token = (
            tokenized_card.update_token()
            .with_payment_method_usage_mode(PaymentMethodUsageMode.MULTIPLE)
            .execute()
        )

        # Validate update response
        self.assertNotEqual(None, response_update_token)
        self.assertEqual("SUCCESS", response_update_token.response_code)
        self.assertEqual("ACTIVE", response_update_token.response_message)
        self.assertEqual(
            PaymentMethodUsageMode.MULTIPLE, response_update_token.token_usage_mode
        )

        # Charge using updated token
        charge_response = (
            tokenized_card.charge(1).with_currency(self.currency).execute()
        )

        # Validate charge response
        self.assertNotEqual(None, charge_response)
        self.assertEqual("SUCCESS", charge_response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, charge_response.response_message)

    def test_card_tokenization_then_update_to_single_usage(self):
        # Create tokenized card with random token ID
        tokenized_card = CreditCardData()
        tokenized_card.token = f"PMT_{GenerationUtils.get_uuid()}"

        # Try to update to single-use mode (should fail)
        try:
            tokenized_card.update_token().with_payment_method_usage_mode(
                PaymentMethodUsageMode.SINGLE
            ).execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("40213", error.response_code)
            self.assertTrue("usage_mode contains unexpected data" in error.message)
            self.assertIsInstance(error, GatewayException)

    def test_card_tokenization_then_update_without_usage_mode(self):
        # Create tokenized card with random token ID
        tokenized_card = CreditCardData()
        tokenized_card.token = f"PMT_{GenerationUtils.get_uuid()}"

        # Try to update without usage mode (should fail)
        try:
            tokenized_card.update_token().execute()
            self.fail("Expected GatewayException was not raised")
        except GatewayException as error:
            self.assertNotEqual(None, error)
            self.assertEqual("50021", error.response_code)
            self.assertEqual(
                "Status Code: MANDATORY_DATA_MISSING - Mandatory Fields missing [card expdate] See Developers Guide",
                error.message,
            )
            self.assertIsInstance(error, GatewayException)
