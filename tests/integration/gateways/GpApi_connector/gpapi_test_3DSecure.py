import unittest
from datetime import datetime

from globalpayments.api import ServicesContainer
from globalpayments.api.entities import Address, ThreeDSecure
from globalpayments.api.entities.browser_data import BrowserData
from globalpayments.api.entities.enums import (
    AddressType,
    AuthenticationSource,
    CardChannel,
    MethodUrlCompletion,
    SdkInterface,
    SdkUiType,
    ColorDepth,
    ChallengeWindowSize,
    Secure3dStatus,
    ThreeDSecureVersion,
    OrderTransactionType,
    ExemptStatus,
)
from globalpayments.api.entities.mobile_data import MobileData
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.payment_methods.credit import CreditCardData
from globalpayments.api.services.secure_3d_service import Secure3dService
from tests.data.GpApi_test_config import GpApiTestConfig
from tests.data.Gpapi_3ds_test_cards import GpApi3DSTestCards
from tests.integration.gateways.three_d_secure_acs_client import ThreeDSecureAcsClient


class GpApi3DSTest(unittest.TestCase):
    """
    3DS authentication tests
    """

    def setUp(self):
        # Set up test configuration
        config = GpApiTestConfig.gpapi_setup_config(CardChannel.CARD_NOT_PRESENT)
        self.gateway_provider = config.gateway_provider
        ServicesContainer.configure(config)

        # Set up test data
        self.currency = "GBP"
        self.amount = 10.01
        self.date = datetime.now()

        # Setup credit card data
        self.card = CreditCardData()
        self.card.exp_month = str(self.date.month).zfill(2)
        self.card.exp_year = str(self.date.year + 1)
        self.card.card_holder_name = "James Mason"
        self.card.cvn = "131"

        # Default card number for challenge required
        self.card.number = GpApi3DSTestCards.CARD_CHALLENGE_REQUIRED_V2_1

        # Setup shipping address
        self.shipping_address = Address()
        self.shipping_address.street_address1 = "Apartment 852"
        self.shipping_address.street_address2 = "Complex 741"
        self.shipping_address.street_address3 = "no"
        self.shipping_address.city = "Chicago"
        self.shipping_address.postal_code = "5001"
        self.shipping_address.state = "IL"
        self.shipping_address.country_code = "840"

        # Setup browser data
        self.browser_data = BrowserData()
        self.browser_data.accept_header = "text/html,application/xhtml+xml,application/xml;q=9,image/webp,img/apng,*/*;q=0.8"
        self.browser_data.color_depth = ColorDepth.TWENTY_FOUR_BITS
        self.browser_data.ip_address = "123.123.123.123"
        self.browser_data.java_enabled = True
        self.browser_data.javascript_enabled = True
        self.browser_data.language = "en"
        self.browser_data.screen_height = 1080
        self.browser_data.screen_width = 1920
        self.browser_data.challenge_window_size = ChallengeWindowSize.WINDOWED_600X400
        self.browser_data.time_zone = "0"
        self.browser_data.user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64, x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"

    def assert_check_enrollment_3ds_v2(self, secure_ecom: ThreeDSecure):
        """Assert 3DS v2 enrollment check response"""
        self.assertIsNotNone(secure_ecom)
        self.assertEqual(Secure3dStatus.ENROLLED.value, secure_ecom.enrolled)
        self.assertEqual(ThreeDSecureVersion.Two, secure_ecom.version)
        self.assertEqual(Secure3dStatus.AVAILABLE.value, secure_ecom.status)
        self.assertIsNotNone(secure_ecom.issuer_acs_url)
        self.assertIsNotNone(secure_ecom.payer_authentication_request)
        self.assertIsNone(secure_ecom.eci or None)

    def assert_initiate_3ds_v2(self, init_auth, is_2point2=False):
        """Assert 3DS v2 initiate authentication response"""
        self.assertIsNotNone(init_auth)
        self.assertEqual(Secure3dStatus.CHALLENGE_REQUIRED.value, init_auth.status)
        self.assertEqual("2.2.0" if is_2point2 else "2.1.0", init_auth.message_version)
        self.assertIsNotNone(init_auth.issuer_acs_url)
        self.assertIsNotNone(init_auth.payer_authentication_request)
        self.assertIsNotNone(init_auth.acs_transaction_id)
        self.assertIsNone(init_auth.eci or None)

    def test_frictionless_full_cycle_v2(self):
        """'frictionless full cycle v2' test"""
        frictionless_successful_3ds_v2_card_tests = {
            "Frictionless v2.1": [
                GpApi3DSTestCards.CARD_AUTH_SUCCESSFUL_V2_1,
                Secure3dStatus.SUCCESS_AUTHENTICATED,
            ],
            "Frictionless no method url v2.1": [
                GpApi3DSTestCards.CARD_AUTH_SUCCESSFUL_NO_METHOD_URL_V2_1,
                Secure3dStatus.SUCCESS_AUTHENTICATED,
            ],
            "Frictionless v2.2": [
                GpApi3DSTestCards.CARD_AUTH_SUCCESSFUL_V2_2,
                Secure3dStatus.SUCCESS_AUTHENTICATED,
            ],
            "Frictionless no method url v2.2": [
                GpApi3DSTestCards.CARD_AUTH_SUCCESSFUL_NO_METHOD_URL_V2_2,
                Secure3dStatus.SUCCESS_AUTHENTICATED,
            ],
        }

        for test_case, (
            card_number,
            expected_status,
        ) in frictionless_successful_3ds_v2_card_tests.items():
            with self.subTest(test_case=test_case):
                self.card.number = card_number

                # Check enrollment
                secure_ecom = (
                    Secure3dService.check_enrollment(self.card)
                    .with_currency(self.currency)
                    .with_amount(self.amount)
                    .execute()
                )

                self.assertIsNotNone(secure_ecom)
                self.assertEqual(Secure3dStatus.ENROLLED.value, secure_ecom.enrolled)
                self.assertEqual(ThreeDSecureVersion.Two, secure_ecom.version)
                self.assertEqual(Secure3dStatus.AVAILABLE.value, secure_ecom.status)

                # Format date for order create date
                formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")

                # Initiate authentication
                init_auth = (
                    Secure3dService.initiate_authentication(self.card, secure_ecom)
                    .with_amount(self.amount)
                    .with_currency(self.currency)
                    .with_authentication_source(AuthenticationSource.Browser)
                    .with_method_url_completion(MethodUrlCompletion.Yes)
                    .with_order_create_date(formatted_date)
                    .with_address(self.shipping_address, AddressType.Shipping)
                    .with_order_transaction_type(
                        OrderTransactionType.GoodsServicePurchase
                    )
                    .with_browser_data(self.browser_data)
                    .execute()
                )

                self.assertIsNotNone(init_auth)
                self.assertEqual(expected_status.value, init_auth.status)

                # Get authentication data
                secure_ecom2 = (
                    Secure3dService.get_authentication_data()
                    .with_server_transaction_id(secure_ecom.server_transaction_id)
                    .with_amount(self.amount)
                    .execute()
                )

                self.card.three_d_secure = secure_ecom2
                self.assertEqual(expected_status.value, secure_ecom2.status)
                self.assertEqual("YES", secure_ecom2.liability_shift)

                # Verify the card
                verify_response = (
                    self.card.verify().with_currency(self.currency).execute()
                )
                self.assertIsNotNone(verify_response)
                self.assertEqual("SUCCESS", verify_response.response_code)
                self.assertEqual("VERIFIED", verify_response.response_message)

                # Process the charge
                transaction = (
                    self.card.charge(self.amount).with_currency(self.currency).execute()
                )

                self.assertIsNotNone(transaction)
                self.assertEqual("SUCCESS", transaction.response_code)
                self.assertEqual(
                    TransactionStatus.CAPTURED, transaction.response_message
                )

    def test_frictionless_full_cycle_v2_failed(self):
        """'frictionless full cycle v2 - failed' test"""
        frictionless_failed_3ds_v2_card_tests = {
            "Frictionless failed 1": [
                GpApi3DSTestCards.CARD_AUTH_ATTEMPTED_BUT_NOT_SUCCESSFUL_V2_1,
                Secure3dStatus.SUCCESS_ATTEMPT_MADE,
            ],
            "Frictionless failed 2": [
                GpApi3DSTestCards.CARD_AUTH_FAILED_V2_1,
                Secure3dStatus.NOT_AUTHENTICATED,
            ],
            "Frictionless failed 3": [
                GpApi3DSTestCards.CARD_AUTH_ISSUER_REJECTED_V2_1,
                Secure3dStatus.FAILED,
            ],
            "Frictionless failed 4": [
                GpApi3DSTestCards.CARD_AUTH_COULD_NOT_BE_PREFORMED_V2_1,
                Secure3dStatus.FAILED,
            ],
            "Frictionless failed 5": [
                GpApi3DSTestCards.CARD_AUTH_ATTEMPTED_BUT_NOT_SUCCESSFUL_V2_2,
                Secure3dStatus.SUCCESS_ATTEMPT_MADE,
            ],
            "Frictionless failed 6": [
                GpApi3DSTestCards.CARD_AUTH_FAILED_V2_2,
                Secure3dStatus.NOT_AUTHENTICATED,
            ],
            "Frictionless failed 7": [
                GpApi3DSTestCards.CARD_AUTH_ISSUER_REJECTED_V2_2,
                Secure3dStatus.FAILED,
            ],
            "Frictionless failed 8": [
                GpApi3DSTestCards.CARD_AUTH_COULD_NOT_BE_PREFORMED_V2_2,
                Secure3dStatus.FAILED,
            ],
        }

        for test_case, (
            card_number,
            expected_status,
        ) in frictionless_failed_3ds_v2_card_tests.items():
            with self.subTest(test_case=test_case):
                self.card.number = card_number

                # Check enrollment
                secure_ecom = (
                    Secure3dService.check_enrollment(self.card)
                    .with_currency(self.currency)
                    .with_amount(self.amount)
                    .execute()
                )

                self.assert_check_enrollment_3ds_v2(secure_ecom)

                # Format date for order create date
                formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")

                # Initiate authentication
                init_auth = (
                    Secure3dService.initiate_authentication(self.card, secure_ecom)
                    .with_amount(self.amount)
                    .with_currency(self.currency)
                    .with_authentication_source(AuthenticationSource.Browser)
                    .with_method_url_completion(MethodUrlCompletion.Yes)
                    .with_order_create_date(formatted_date)
                    .with_address(self.shipping_address, AddressType.Shipping)
                    .with_browser_data(self.browser_data)
                    .execute()
                )

                self.assertIsNotNone(init_auth)
                self.assertEqual(expected_status.value, init_auth.status)

                # Get authentication data
                secure_ecom2 = (
                    Secure3dService.get_authentication_data()
                    .with_server_transaction_id(secure_ecom.server_transaction_id)
                    .with_amount(self.amount)
                    .execute()
                )

                # Determine expected liability shift
                liability_shift = (
                    "YES"
                    if expected_status == Secure3dStatus.SUCCESS_ATTEMPT_MADE
                    else "NO"
                )

                self.card.three_d_secure = secure_ecom2
                self.assertEqual(expected_status.value, secure_ecom2.status)
                self.assertEqual(liability_shift, secure_ecom2.liability_shift)

                # Process the charge
                transaction = (
                    self.card.charge(self.amount).with_currency(self.currency).execute()
                )

                self.assertIsNotNone(transaction)
                self.assertEqual("SUCCESS", transaction.response_code)
                self.assertEqual(
                    TransactionStatus.CAPTURED, transaction.response_message
                )

    def test_card_holder_enrolled_challenge_required_v2(self):
        """'card holder enrolled - challenge required - v2' test"""
        challenge_successful_3ds_v2_card_tests = {
            "Challenge v2.1": [
                GpApi3DSTestCards.CARD_CHALLENGE_REQUIRED_V2_1,
                Secure3dStatus.SUCCESS_AUTHENTICATED,
            ],
            "Challenge v2.2": [
                GpApi3DSTestCards.CARD_CHALLENGE_REQUIRED_V2_2,
                Secure3dStatus.SUCCESS_AUTHENTICATED,
            ],
        }

        for test_case, (
            card_number,
            expected_status,
        ) in challenge_successful_3ds_v2_card_tests.items():
            with self.subTest(test_case=test_case):
                self.card.number = card_number

                # Check enrollment
                secure_ecom = (
                    Secure3dService.check_enrollment(self.card)
                    .with_currency(self.currency)
                    .with_amount(self.amount)
                    .execute()
                )

                self.assert_check_enrollment_3ds_v2(secure_ecom)

                # Format date for order create date
                formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")

                # Initiate authentication
                init_auth = (
                    Secure3dService.initiate_authentication(self.card, secure_ecom)
                    .with_amount(self.amount)
                    .with_currency(self.currency)
                    .with_authentication_source(AuthenticationSource.Browser)
                    .with_method_url_completion(MethodUrlCompletion.Yes)
                    .with_order_create_date(formatted_date)
                    .with_address(self.shipping_address, AddressType.Shipping)
                    .with_browser_data(self.browser_data)
                    .execute()
                )

                self.assertIsNotNone(init_auth)
                self.assertEqual(
                    Secure3dStatus.CHALLENGE_REQUIRED.value, init_auth.status
                )
                self.assertIsNotNone(init_auth.issuer_acs_url)
                self.assertIsNotNone(init_auth.payer_authentication_request)

                # Authenticate through ACS
                auth_client = ThreeDSecureAcsClient(secure_ecom.issuer_acs_url)
                auth_client.set_gateway_provider(self.gateway_provider)
                auth_response = auth_client.authenticate_v2(init_auth)

                self.assertTrue(auth_response.get_status())
                self.assertIsNotNone(auth_response.get_merchant_data())

                # Get authentication data
                secure_ecom2 = (
                    Secure3dService.get_authentication_data()
                    .with_server_transaction_id(auth_response.get_merchant_data())
                    .with_amount(self.amount)
                    .execute()
                )

                self.card.three_d_secure = secure_ecom2
                self.assertEqual(expected_status.value, secure_ecom2.status)
                self.assertEqual("YES", secure_ecom2.liability_shift)

                # Process the charge
                transaction = (
                    self.card.charge(self.amount).with_currency(self.currency).execute()
                )

                self.assertIsNotNone(transaction)
                self.assertEqual("SUCCESS", transaction.response_code)
                self.assertEqual(
                    TransactionStatus.CAPTURED, transaction.response_message
                )

    def test_full_cycle_with_card_tokenization_v2(self):
        """'full cycle with card tokenization v2' test"""
        self.card.number = GpApi3DSTestCards.CARD_AUTH_SUCCESSFUL_V2_1

        # Tokenize the card
        response = self.card.tokenize().execute()
        token_id = response.token

        # Create a tokenized card
        tokenized_card = CreditCardData()
        tokenized_card.token = token_id
        tokenized_card.card_holder_name = "James Mason"

        # Check enrollment
        secure_ecom = (
            Secure3dService.check_enrollment(tokenized_card)
            .with_currency(self.currency)
            .with_amount(self.amount)
            .execute()
        )

        self.assert_check_enrollment_3ds_v2(secure_ecom)

        # Format date for order create date
        formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")

        # Initiate authentication
        init_auth = (
            Secure3dService.initiate_authentication(self.card, secure_ecom)
            .with_amount(self.amount)
            .with_currency(self.currency)
            .with_authentication_source(AuthenticationSource.Browser)
            .with_method_url_completion(MethodUrlCompletion.Yes)
            .with_order_create_date(formatted_date)
            .with_address(self.shipping_address, AddressType.Shipping)
            .with_order_transaction_type(OrderTransactionType.GoodsServicePurchase)
            .with_browser_data(self.browser_data)
            .execute()
        )

        self.assertIsNotNone(init_auth)
        self.assertEqual(Secure3dStatus.SUCCESS_AUTHENTICATED.value, secure_ecom.status)
        self.assertEqual("YES", secure_ecom.liability_shift)

        # Get authentication data
        secure_ecom2 = (
            Secure3dService.get_authentication_data()
            .with_server_transaction_id(secure_ecom.server_transaction_id)
            .with_amount(self.amount)
            .execute()
        )

        self.assertEqual(
            Secure3dStatus.SUCCESS_AUTHENTICATED.value, secure_ecom2.status
        )
        self.assertEqual("YES", secure_ecom2.liability_shift)

        tokenized_card.three_d_secure = secure_ecom2

        # Verify the card
        verify_response = self.card.verify().with_currency(self.currency).execute()
        self.assertIsNotNone(verify_response)
        self.assertEqual("SUCCESS", verify_response.response_code)
        self.assertEqual("VERIFIED", verify_response.response_message)

        # Process the charge
        transaction = (
            self.card.charge(self.amount).with_currency(self.currency).execute()
        )

        self.assertIsNotNone(transaction)
        self.assertEqual("SUCCESS", transaction.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, transaction.response_message)

    def test_exemption_sale_transaction(self):
        """'exemption sale transaction' test"""
        self.card.number = GpApi3DSTestCards.CARD_CHALLENGE_REQUIRED_V2_2

        three_ds = ThreeDSecure()
        three_ds.exempt_status = ExemptStatus.LOW_VALUE
        self.card.three_d_secure = three_ds

        response = self.card.charge(self.amount).with_currency(self.currency).execute()

        self.assertIsNotNone(response)
        self.assertEqual("SUCCESS", response.response_code)
        self.assertEqual(TransactionStatus.CAPTURED, response.response_message)

    def test_challenge_required_v2_initiate_with_mobile_sdk(self):
        """mobile SDK test"""
        self.card.number = GpApi3DSTestCards.CARD_CHALLENGE_REQUIRED_V2_2

        # Check enrollment
        secure_ecom = (
            Secure3dService.check_enrollment(self.card)
            .with_currency(self.currency)
            .with_amount(self.amount)
            .execute()
        )

        self.assert_check_enrollment_3ds_v2(secure_ecom)

        # Setup mobile data
        mobile_data = MobileData()
        mobile_data.encoded_data = "ew0KCSJEViI6ICIxLjAiLA0KCSJERCI6IHsNCgkJIkMwMDEiOiAiQW5kcm9pZCIsDQoJCSJDMDAyIjogIkhUQyBPbmVfTTgiLA0KCQkiQzAwNCI6ICI1LjAuMSIsDQoJCSJDMDA1IjogImVuX1VTIiwNCgkJIkMwMDYiOiAiRWFzdGVybiBTdGFuZGFyZCBUaW1lIiwNCgkJIkMwMDciOiAiMDY3OTc5MDMtZmI2MS00MWVkLTk0YzItNGQyYjc0ZTI3ZDE4IiwNCgkJIkMwMDkiOiAiSm9obidzIEFuZHJvaWQgRGV2aWNlIg0KCX0sDQoJIkRQTkEiOiB7DQoJCSJDMDEwIjogIlJFMDEiLA0KCQkiQzAxMSI6ICJSRTAzIg0KCX0sDQoJIlNXIjogWyJTVzAxIiwgIlNXMDQiXQ0KfQ0K"
        mobile_data.application_reference = "f283b3ec-27da-42a1-acea-f3f70e75bbdc"
        mobile_data.sdk_interface = SdkInterface.Both
        mobile_data.sdk_ui_types = [SdkUiType.Oob]
        mobile_data.ephemeral_public_key = """{"kty": "EC","crv": "P-256","x": "WWcpTjbOqiu_1aODllw5rYTq5oLXE_T0huCPjMIRbkI","y": "Wz_7anIeadV8SJZUfr4drwjzuWoUbOsHp5GdRZBAAiw"}"""
        mobile_data.maximum_timeout = 50
        mobile_data.reference_number = "3DS_LOA_SDK_PPFU_020100_00007"
        mobile_data.sdk_trans_reference = "b2385523-a66c-4907-ac3c-91848e8c0067"

        # Format date for order create date
        formatted_date = self.date.strftime("%Y-%m-%d %H:%M:%S")

        # Initiate authentication with mobile SDK
        response = (
            Secure3dService.initiate_authentication(self.card, secure_ecom)
            .with_amount(self.amount)
            .with_currency(self.currency)
            .with_authentication_source(AuthenticationSource.MobileSdk)
            .with_mobile_data(mobile_data)
            .with_method_url_completion(MethodUrlCompletion.Yes)
            .with_order_create_date(formatted_date)
            .with_address(self.shipping_address, AddressType.Shipping)
            .execute()
        )

        self.assertIsNotNone(response)
        self.assert_initiate_3ds_v2(response, True)

        self.assertIsNotNone(response.payer_authentication_request)
        self.assertIsNotNone(response.acs_interface)
        self.assertIsNotNone(response.acs_ui_template)
        self.assertIsNotNone(response.provider_server_trans_ref)
        self.assertEqual("NATIVE", response.acs_interface)
        self.assertEqual("OUT_OF_BAND", response.acs_ui_template)
