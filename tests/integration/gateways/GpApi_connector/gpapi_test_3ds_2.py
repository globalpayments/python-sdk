# import unittest
# import uuid
# from datetime import datetime
#
# from globalpayments.api import ServicesContainer
# from globalpayments.api.entities import Address, ThreeDSecure
# from globalpayments.api.entities.browser_data import BrowserData
# from globalpayments.api.entities.enums import (
#     AddressType,
#     AuthenticationSource,
#     CardChannel,
#     ChallengeRequestIndicator,
#     MethodUrlCompletion,
#     SdkInterface,
#     SdkUiType,
#     StoredCredentialInitiator,
#     StoredCredentialReason,
#     StoredCredentialSequence,
#     StoredCredentialType,
#     ColorDepth,
#     ChallengeWindowSize,
#     Secure3dStatus,
#     ThreeDSecureVersion,
# )
# from globalpayments.api.entities.exceptions import BuilderException, GatewayException
# from globalpayments.api.entities.mobile_data import MobileData
# from globalpayments.api.entities.stored_credentials import StoredCredential
# from globalpayments.api.entities.transaction_status import TransactionStatus
# from globalpayments.api.payment_methods.credit import CreditCardData
# from globalpayments.api.services.secure_3d_service import Secure3dService
# from tests.data.GpApi_test_config import GpApiTestConfig
# from tests.integration.gateways.three_d_secure_acs_client import ThreeDSecureAcsClient
#
#
# class GpApi3DSTest(unittest.TestCase):
#     """
#     Test 3DS authentication features with GpApi
#     """
#
#     def setUp(self):
#         # Set up test configuration
#         config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_NOT_PRESENT)
#         self.gateway_provider = config.gateway_provider
#         ServicesContainer.configure(config)
#
#         # Set up test data
#         self.currency = "GBP"
#         self.amount = 10.01
#         self.date = datetime.now()
#
#         # Setup credit card data
#         self.card = CreditCardData()
#         self.card.exp_month = str(self.date.month).zfill(2)
#         self.card.exp_year = str(self.date.year + 1)
#         self.card.card_holder_name = "James Mason"
#
#         # Set card number for challenge required
#         self.card.number = (
#             "4263970000005262"  # GpApi 3DS test card for challenge required
#         )
#
#         # Setup shipping address
#         self.shipping_address = Address()
#         self.shipping_address.street_address1 = "Apartment 852"
#         self.shipping_address.street_address2 = "Complex 741"
#         self.shipping_address.street_address3 = "no"
#         self.shipping_address.city = "Chicago"
#         self.shipping_address.postal_code = "5001"
#         self.shipping_address.state = "IL"
#         self.shipping_address.country_code = "840"
#
#         # Setup browser data
#         self.browser_data = BrowserData()
#         self.browser_data.accept_header = "text/html,application/xhtml+xml,application/xml;q=9,image/webp,img/apng,*/*;q=0.8"
#         self.browser_data.color_depth = ColorDepth.TWENTY_FOUR_BITS
#         self.browser_data.ip_address = "123.123.123.123"
#         self.browser_data.java_enabled = True
#         self.browser_data.javascript_enabled = True
#         self.browser_data.language = "en"
#         self.browser_data.screen_height = 1080
#         self.browser_data.screen_width = 1920
#         self.browser_data.challenge_window_size = ChallengeWindowSize.WINDOWED_600X400
#         self.browser_data.time_zone = "0"
#         self.browser_data.user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64, x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
#
#     def assert_check_enrollment_3ds_v2(self, secure_ecom: ThreeDSecure):
#         """Assert 3DS v2 enrollment check response"""
#         self.assertIsNotNone(secure_ecom)
#         self.assertEqual(Secure3dStatus.ENROLLED, secure_ecom.enrolled)
#         self.assertEqual(ThreeDSecureVersion.Two, secure_ecom.version)
#         self.assertEqual(Secure3dStatus.AVAILABLE, secure_ecom.status)
#         self.assertIsNotNone(secure_ecom.issuer_acs_url)
#         self.assertIsNotNone(secure_ecom.payer_authentication_request)
#         self.assertIsNone(secure_ecom.eci)
#
#     def assert_initiate_3ds_v2(self, init_auth):
#         """Assert 3DS v2 initiate authentication response"""
#         self.assertIsNotNone(init_auth)
#         self.assertEqual(Secure3dStatus.CHALLENGE_REQUIRED, init_auth.status)
#         self.assertEqual("2.1.0", init_auth.message_version)
#
#     def test_full_cycle_v2_frictionless(self):
#         """Test the full authentication cycle for frictionless flow"""
#         # Use auth successful test card
#         self.card.number = (
#             "4263970000005262"  # Replace with your frictionless success card
#         )
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#         # Format date for order create date
#         formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Initiate authentication
#         init_auth = (
#             Secure3dService.initiate_authentication(self.card, secure_ecom)
#             .with_amount(self.amount)
#             .with_currency(self.currency)
#             .with_authentication_source(AuthenticationSource.Browser)
#             .with_method_url_completion(MethodUrlCompletion.Yes)
#             .with_order_create_date(formatted_date)
#             .with_address(self.shipping_address, AddressType.Shipping)
#             .with_browser_data(self.browser_data)
#             .execute()
#         )
#
#         self.assertIsNotNone(init_auth)
#         self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED, init_auth.status)
#         self.assertEqual("YES", init_auth.liability_shift)
#
#         # Get authentication data
#         secure_ecom2 = (
#             Secure3dService.get_authentication_data()
#             .with_server_transaction_id(secure_ecom.server_transaction_id)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.card.three_d_secure = secure_ecom2
#         self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED, secure_ecom2.status)
#
#         # Process the charge
#         transaction = (
#             self.card.charge(self.amount).with_currency(self.currency).execute()
#         )
#
#         self.assertIsNotNone(transaction)
#         self.assertEqual("SUCCESS", transaction.response_code)
#         self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)
#
#     def test_full_cycle_v2_frictionless_failed(self):
#         """Test the full authentication cycle for frictionless flow with failed authentication"""
#         # Use auth failed test card
#         self.card.number = (
#             "4222000006285344"  # Replace with your frictionless failure card
#         )
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#         # Format date for order create date
#         formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Initiate authentication
#         init_auth = (
#             Secure3dService.initiate_authentication(self.card, secure_ecom)
#             .with_amount(self.amount)
#             .with_currency(self.currency)
#             .with_authentication_source(AuthenticationSource.Browser)
#             .with_method_url_completion(MethodUrlCompletion.Yes)
#             .with_order_create_date(formatted_date)
#             .with_address(self.shipping_address, AddressType.Shipping)
#             .with_browser_data(self.browser_data)
#             .execute()
#         )
#
#         self.assertIsNotNone(init_auth)
#         self.assertEqual(Secure3dStatus.NOT_AUTHENTICATED, init_auth.status)
#         self.assertNotEqual("YES", init_auth.liability_shift)
#
#         # Get authentication data
#         secure_ecom2 = (
#             Secure3dService.get_authentication_data()
#             .with_server_transaction_id(secure_ecom.server_transaction_id)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.card.three_d_secure = secure_ecom2
#         self.assertEqual(Secure3dStatus.NOT_AUTHENTICATED, secure_ecom2.status)
#
#         # Process the charge
#         transaction = (
#             self.card.charge(self.amount).with_currency(self.currency).execute()
#         )
#
#         self.assertIsNotNone(transaction)
#         self.assertEqual("SUCCESS", transaction.response_code)
#         self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)
#
#     def test_full_cycle_v2_frictionless_with_card_tokenization(self):
#         """Test full authentication cycle with tokenized card"""
#         # Use auth successful test card
#         self.card.number = (
#             "4263970000005262"  # Replace with your frictionless success card
#         )
#
#         # Tokenize the card
#         tokenize_response = self.card.tokenize().execute()
#         token_id = tokenize_response.token
#
#         # Create a tokenized card
#         tokenized_card = CreditCardData()
#         tokenized_card.token = token_id
#         tokenized_card.card_holder_name = "James Mason"
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(tokenized_card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#         self.assertIsNotNone(secure_ecom.payer_authentication_request)
#
#         # Format date for order create date
#         formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Initiate authentication
#         init_auth = (
#             Secure3dService.initiate_authentication(tokenized_card, secure_ecom)
#             .with_amount(self.amount)
#             .with_currency(self.currency)
#             .with_authentication_source(AuthenticationSource.Browser)
#             .with_method_url_completion(MethodUrlCompletion.Yes)
#             .with_order_create_date(formatted_date)
#             .with_address(self.shipping_address, AddressType.Shipping)
#             .with_browser_data(self.browser_data)
#             .execute()
#         )
#
#         self.assertIsNotNone(init_auth)
#         self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED, init_auth.status)
#         self.assertEqual("YES", init_auth.liability_shift)
#
#         # Get authentication data
#         secure_ecom2 = (
#             Secure3dService.get_authentication_data()
#             .with_server_transaction_id(secure_ecom.server_transaction_id)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.card.three_d_secure = secure_ecom2
#         self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED, secure_ecom2.status)
#
#         # Process the charge
#         transaction = (
#             self.card.charge(self.amount).with_currency(self.currency).execute()
#         )
#
#         self.assertIsNotNone(transaction)
#         self.assertEqual("SUCCESS", transaction.response_code)
#         self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)
#
#     def test_full_cycle_v2_card_holder_enrolled_challenge_required(self):
#         """Test full authentication cycle with card holder enrolled and challenge required"""
#         # Use challenge required test card
#         self.card.number = (
#             "4222000006285344"  # Replace with your challenge required card
#         )
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#         # Format date for order create date
#         formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Initiate authentication
#         response = (
#             Secure3dService.initiate_authentication(self.card, secure_ecom)
#             .with_amount(self.amount)
#             .with_currency(self.currency)
#             .with_authentication_source(AuthenticationSource.Browser)
#             .with_method_url_completion(MethodUrlCompletion.Yes)
#             .with_order_create_date(formatted_date)
#             .with_address(self.shipping_address, AddressType.Shipping)
#             .with_browser_data(self.browser_data)
#             .execute()
#         )
#
#         self.assertIsNotNone(response)
#         self.assert_initiate_3ds_v2(response)
#         self.assertEqual(Secure3dStatus.CHALLENGE_REQUIRED, response.status)
#         self.assertIsNotNone(response.payer_authentication_request)
#         self.assertIsNotNone(response.issuer_acs_url)
#
#         # Authenticate through ACS
#         auth_client = ThreeDSecureAcsClient(secure_ecom.issuer_acs_url)
#         auth_client.set_gateway_provider(self.gateway_provider)
#         auth_response = auth_client.authenticate_v2(response)
#
#         self.assertTrue(auth_response.get_status())
#         self.assertIsNotNone(auth_response.get_merchant_data())
#
#         # Get authentication data
#         secure_ecom2 = (
#             Secure3dService.get_authentication_data()
#             .with_server_transaction_id(auth_response.get_merchant_data())
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.card.three_d_secure = secure_ecom2
#         self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED, secure_ecom2.status)
#
#         # Process the charge
#         transaction = (
#             self.card.charge(self.amount).with_currency(self.currency).execute()
#         )
#
#         self.assertIsNotNone(transaction)
#         self.assertEqual("SUCCESS", transaction.response_code)
#         self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)
#
#     def test_card_holder_enrolled_challenge_required_v2_2(self):
#         """Test card holder enrolled with challenge required v2.2"""
#         # Use challenge required test card
#         self.card.number = (
#             "4222000006285344"  # Replace with your challenge required card
#         )
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#     def test_card_holder_enrolled_challenge_required_v2_with_idempotency_key(self):
#         """Test card holder enrolled with challenge required v2 and idempotency key"""
#         # Use challenge required test card
#         self.card.number = (
#             "4222000006285344"  # Replace with your challenge required card
#         )
#
#         # Generate idempotency key
#         idempotency_key = str(uuid.uuid4())
#
#         # Check enrollment with idempotency key
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_idempotency_key(idempotency_key)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#         # Try again with same idempotency key, should fail
#         with self.assertRaises(GatewayException) as context:
#             Secure3dService.check_enrollment(self.card).with_currency(
#                 self.currency
#             ).with_idempotency_key(idempotency_key).with_amount(self.amount).execute()
#
#         self.assertEqual("40039", context.exception.response_code)
#         self.assertTrue(
#             "Idempotency Key seen before" in context.exception.response_message
#         )
#
#     def test_card_holder_enrolled_challenge_required_v2_with_tokenized_card(self):
#         """Test card holder enrolled with challenge required v2 and tokenized card"""
#         # Tokenize the card
#         response = self.card.tokenize().execute()
#
#         tokenized_card = CreditCardData()
#         tokenized_card.token = response.token
#         tokenized_card.card_holder_name = "James Mason"
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#     def test_card_holder_enrolled_challenge_required_v2_all_preference_value(self):
#         """Test card holder enrolled with challenge required v2 and all preference values"""
#         for value in ChallengeRequestIndicator:
#             secure_ecom = (
#                 Secure3dService.check_enrollment(self.card)
#                 .with_currency(self.currency)
#                 .with_amount(self.amount)
#                 .with_challenge_request_indicator(value)
#                 .execute()
#             )
#
#             self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#     def test_card_holder_enrolled_challenge_required_v2_stored_credentials(self):
#         """Test card holder enrolled with challenge required v2 and stored credentials"""
#         stored_credentials = StoredCredential()
#         stored_credentials.initiator = StoredCredentialInitiator.Merchant
#         stored_credentials.type = StoredCredentialType.INSTALLMENT
#         stored_credentials.sequence = StoredCredentialSequence.SUBSEQUENT
#         stored_credentials.reason = StoredCredentialReason.INCREMENTAL
#
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .with_stored_credential(stored_credentials)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#     def test_card_holder_enrolled_challenge_required_v2_all_sources(self):
#         """Test card holder enrolled with challenge required v2 and all sources"""
#         for value in AuthenticationSource:
#             secure_ecom = (
#                 Secure3dService.check_enrollment(self.card)
#                 .with_currency(self.currency)
#                 .with_amount(self.amount)
#                 .with_authentication_source(value)
#                 .execute()
#             )
#
#             self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#     def test_card_holder_enrolled_challenge_required_v2_with_null_payment_method(self):
#         """Test card holder enrolled with challenge required v2 and null payment method"""
#         with self.assertRaises(BuilderException) as context:
#             Secure3dService.check_enrollment(self.card).with_currency(
#                 self.currency
#             ).with_payment_method(None).with_amount(self.amount).execute()
#
#         self.assertTrue(
#             "paymentMethod cannot be null for this transaction type"
#             in context.exception.message
#         )
#
#     def test_card_holder_enrolled_frictionless_v2(self):
#         """Test card holder enrolled with frictionless v2"""
#         # Use auth successful test card
#         self.card.number = (
#             "4263970000005262"  # Replace with your frictionless success card
#         )
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#     def test_card_holder_challenge_required_post_result(self):
#         """Test card holder challenge required post result"""
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#         self.assertEqual(Secure3dStatus.ENROLLED, secure_ecom.enrolled)
#         self.assertEqual(ThreeDSecureVersion.Two, secure_ecom.version)
#         self.assertEqual(Secure3dStatus.AVAILABLE, secure_ecom.status)
#
#         # Format date for order create date
#         formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Initiate authentication
#         init_auth = (
#             Secure3dService.initiate_authentication(self.card, secure_ecom)
#             .with_amount(self.amount)
#             .with_currency(self.currency)
#             .with_authentication_source(AuthenticationSource.Browser)
#             .with_method_url_completion(MethodUrlCompletion.Yes)
#             .with_order_create_date(formatted_date)
#             .with_address(self.shipping_address, AddressType.Shipping)
#             .with_browser_data(self.browser_data)
#             .execute()
#         )
#
#         self.assertIsNotNone(init_auth)
#         self.assertEqual(Secure3dStatus.CHALLENGE_REQUIRED, init_auth.status)
#         self.assertIsNotNone(init_auth.issuer_acs_url)
#         self.assertIsNotNone(init_auth.payer_authentication_request)
#
#         # Authenticate through ACS
#         auth_client = ThreeDSecureAcsClient(secure_ecom.issuer_acs_url)
#         auth_client.set_gateway_provider(self.gateway_provider)
#         auth_response = auth_client.authenticate_v2(init_auth)
#
#         self.assertTrue(auth_response.get_status())
#         self.assertIsNotNone(auth_response.get_merchant_data())
#
#         # Get authentication data
#         secure_ecom2 = (
#             Secure3dService.get_authentication_data()
#             .with_server_transaction_id(auth_response.get_merchant_data())
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.card.three_d_secure = secure_ecom2
#         self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED, secure_ecom2.status)
#         self.assertEqual("05", str(secure_ecom2.eci))
#         self.assertEqual("2.1.0", secure_ecom2.message_version)
#         self.assertIsNotNone(secure_ecom2.acs_transaction_id)
#         self.assertIsNotNone(secure_ecom2.server_transaction_id)
#         self.assertIsNotNone(secure_ecom2.directory_server_transaction_id)
#
#     def test_challenge_required_v2_initiate_with_mobile_sdk(self):
#         """Test challenge required v2 initiate with mobile SDK"""
#         # Use challenge required test card
#         self.card.number = (
#             "4222000006285344"  # Replace with your challenge required card
#         )
#
#         # Check enrollment
#         secure_ecom = (
#             Secure3dService.check_enrollment(self.card)
#             .with_currency(self.currency)
#             .with_amount(self.amount)
#             .execute()
#         )
#
#         self.assert_check_enrollment_3ds_v2(secure_ecom)
#
#         # Setup mobile data
#         mobile_data = MobileData()
#         mobile_data.encoded_data = "ew0KCSJEViI6ICIxLjAiLA0KCSJERCI6IHsNCgkJIkMwMDEiOiAiQW5kcm9pZCIsDQoJCSJDMDAyIjogIkhUQyBPbmVfTTgiLA0KCQkiQzAwNCI6ICI1LjAuMSIsDQoJCSJDMDA1IjogImVuX1VTIiwNCgkJIkMwMDYiOiAiRWFzdGVybiBTdGFuZGFyZCBUaW1lIiwNCgkJIkMwMDciOiAiMDY3OTc5MDMtZmI2MS00MWVkLTk0YzItNGQyYjc0ZTI3ZDE4IiwNCgkJIkMwMDkiOiAiSm9obidzIEFuZHJvaWQgRGV2aWNlIg0KCX0sDQoJIkRQTkEiOiB7DQoJCSJDMDEwIjogIlJFMDEiLA0KCQkiQzAxMSI6ICJSRTAzIg0KCX0sDQoJIlNXIjogWyJTVzAxIiwgIlNXMDQiXQ0KfQ0K"
#         mobile_data.application_reference = "f283b3ec-27da-42a1-acea-f3f70e75bbdc"
#         mobile_data.sdk_interface = SdkInterface.Both
#         mobile_data.sdk_ui_types = [SdkUiType.Oob]
#         mobile_data.ephemeral_public_key = """{"kty": "EC","crv": "P-256","x": "WWcpTjbOqiu_1aODllw5rYTq5oLXE_T0huCPjMIRbkI","y": "Wz_7anIeadV8SJZUfr4drwjzuWoUbOsHp5GdRZBAAiw"}"""
#         mobile_data.maximum_timeout = 50
#         mobile_data.reference_number = "3DS_LOA_SDK_PPFU_020100_00007"
#         mobile_data.sdk_trans_reference = "b2385523-a66c-4907-ac3c-91848e8c0067"
#
#         # Format date for order create date
#         formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")
#
#         # Initiate authentication
#         response = (
#             Secure3dService.initiate_authentication(self.card, secure_ecom)
#             .with_amount(self.amount)
#             .with_currency(self.currency)
#             .with_authentication_source(AuthenticationSource.MobileSdk)
#             .with_mobile_data(mobile_data)
#             .with_method_url_completion(MethodUrlCompletion.Yes)
#             .with_order_create_date(formatted_date)
#             .with_address(self.shipping_address, AddressType.Shipping)
#             .execute()
#         )
#
#         self.assertIsNotNone(response)
#         self.assert_initiate_3ds_v2(response)
#
#         self.assertIsNotNone(response.payer_authentication_request)
#         self.assertIsNotNone(response.acs_interface)
#         self.assertIsNotNone(response.acs_ui_template)
#         self.assertIsNotNone(response.provider_server_trans_ref)
#         self.assertEqual("NATIVE", response.acs_interface)
#         self.assertEqual("OUT_OF_BAND", response.acs_ui_template)
