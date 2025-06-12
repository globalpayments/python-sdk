"""
Mapping utility for GP API responses
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional, Union

from globalpayments.api.entities import (
    Transaction,
    Address,
    TransactionSummary,
    ApiException,
    ThreeDSecure,
)
from globalpayments.api.entities.alternative_payment_response import (
    AlternativePaymentResponse,
)
from globalpayments.api.entities.card import Card
from globalpayments.api.entities.card_issuer_response import CardIssuerResponse
from globalpayments.api.entities.dcc_rate_data import DccRateData
from globalpayments.api.entities.dispute_document import DisputeDocument
from globalpayments.api.entities.enums import (
    CaptureMode,
    PaymentProvider,
    PaymentMethodType,
    AddressType,
    ReportType,
    PaymentMethodName,
    ThreeDSecureVersion,
    AuthenticationSource,
    Secure3dStatus,
)
from globalpayments.api.entities.gp_api import PagedResult
from globalpayments.api.entities.gp_api.DTO.payment_method import PaymentMethod
from globalpayments.api.entities.message_extension import MessageExtension
from globalpayments.api.entities.payer_details import PayerDetails
from globalpayments.api.entities.reporting import (
    StoredPaymentMethodSummary,
    DepositSummary,
    DisputeSummary,
)
from globalpayments.api.entities.transaction_status import TransactionStatus
from globalpayments.api.utils import StringUtils


class GpApiMapping:
    """
    Mapping utility for GP API responses
    """

    DCC_RESPONSE = "RATE_LOOKUP"

    @staticmethod
    def map_response(response: Dict[str, Any]) -> Transaction:
        """
        Maps API response to Transaction object

        @param response: The API response
        @return: Mapped Transaction object
        """
        transaction = Transaction()

        if not response:
            return transaction

        transaction.response_code = response.get("action", {}).get("result_code")
        transaction.response_message = response.get("status")

        transaction.transaction_id = response.get("id")
        transaction.client_transaction_id = response.get("reference")
        transaction.timestamp = response.get("time_created", "")
        transaction.reference_number = response.get("reference")

        transaction.balance_amount = StringUtils.to_amount(response.get("amount"))
        if response.get("status") == TransactionStatus.PREAUTHORIZED and response.get(
            "amount"
        ):
            transaction.authorized_amount = StringUtils.to_amount(
                response.get("amount")
            )

        transaction.multi_capture = (
            response.get("capture_mode")
            and response.get("capture_mode") == CaptureMode.MULTIPLE
        )
        transaction.fingerprint = response.get("fingerprint")
        transaction.fingerprint_indicator = response.get(
            "fingerprint_presence_indicator"
        )

        transaction.token = (
            response.get("id")
            if response.get("id", "").startswith(
                PaymentMethod.PAYMENT_METHOD_TOKEN_PREFIX
            )
            else None
        )
        transaction.token_usage_mode = response.get("usage_mode")

        if response.get("payment_method"):
            GpApiMapping._map_payment_method_transaction_details(
                transaction, response.get("payment_method", {})
            )

        if response.get("card"):
            card_details = Card()
            card_details.card_number = response.get("card", {}).get("number")
            card_details.brand = response.get("card", {}).get("brand")
            card_details.card_exp_month = response.get("card", {}).get("expiry_month")
            card_details.card_exp_year = response.get("card", {}).get("expiry_year")

            transaction.card_details = card_details
            transaction.card_type = response.get("card", {}).get("brand", "")
            transaction.cvn_response_code = response.get("card", {}).get("cvv")
            transaction.card_brand_transaction_id = response.get("card", {}).get(
                "brand_reference"
            )

        if response.get("action", {}).get(
            "type"
        ) == GpApiMapping.DCC_RESPONSE or response.get("currency_conversion"):
            transaction.dcc_rate_data = GpApiMapping._map_dcc_info(response)

        return transaction

    @staticmethod
    def _map_payment_method_transaction_details(
        transaction: Transaction, payment_method_response: Dict[str, Any]
    ) -> None:
        """
        Maps payment method details to transaction

        @param transaction: Transaction to update
        @param payment_method_response: Payment method response data
        """
        card_issuer_response = CardIssuerResponse()
        card_issuer_response.result = payment_method_response.get("result")

        if payment_method_response.get("id"):
            transaction.token = payment_method_response.get("id")

        transaction.fingerprint = payment_method_response.get("fingerprint")
        transaction.fingerprint_indicator = payment_method_response.get(
            "fingerprint_presence_indicator"
        )

        if payment_method_response.get("card"):
            card = payment_method_response.get("card", {})
            card_details = Card()
            card_details.masked_number_last4 = card.get("masked_number_last4")
            card_details.brand = card.get("brand")
            transaction.card_details = card_details

            transaction.card_last4 = card.get("masked_number_last4")
            transaction.card_type = card.get("brand")
            transaction.cvn_response_code = card.get("cvv")
            transaction.cvn_response_message = card.get("cvv_result")
            transaction.card_brand_transaction_id = card.get("brand_reference")
            transaction.avs_response_code = card.get("avs_postal_code_result")
            transaction.avs_address_response = card.get("avs_address_result")
            transaction.avs_response_message = card.get("avs_action")
            transaction.authorization_code = card.get("authcode")

            if card.get("provider"):
                card_issuer_response = GpApiMapping._map_card_issuer_response(
                    card.get("provider", {})
                )

        transaction.card_issuer_response = card_issuer_response

        if (
            payment_method_response.get("apm")
            and payment_method_response.get("apm", {}).get("provider")
            == PaymentProvider.OPEN_BANKING.value.lower()
        ):
            pass
        elif payment_method_response.get("bank_transfer"):
            bank_transfer = payment_method_response.get("bank_transfer", {})
            transaction.account_number_last4 = bank_transfer.get(
                "masked_account_number_last4"
            )
            transaction.account_type = bank_transfer.get("account_type")
            transaction.payment_method_type = PaymentMethodType.ACH
        elif payment_method_response.get("apm"):
            transaction.payment_method_type = PaymentMethodType.APM

        if payment_method_response.get(
            "shipping_address"
        ) or payment_method_response.get("payer"):
            payer_details = PayerDetails()
            payer_details.email = payment_method_response.get("payer", {}).get("email")

            if payment_method_response.get("payer", {}).get("billing_address"):
                billing_address = payment_method_response.get("payer", {}).get(
                    "billing_address", {}
                )
                payer_details.first_name = billing_address.get("first_name")
                payer_details.last_name = billing_address.get("last_name")
                payer_details.billing_address = GpApiMapping._map_address_object(
                    billing_address, AddressType.Billing
                )

            payer_details.shipping_address = GpApiMapping._map_address_object(
                payment_method_response.get("shipping_address", {}),
                AddressType.Shipping,
            )
            transaction.payer_details = payer_details

    @staticmethod
    def _map_card_issuer_response(card_provider: Dict[str, Any]) -> CardIssuerResponse:
        """
        Maps provider data to CardIssuerResponse

        @param card_provider: Provider response data
        @return: Mapped CardIssuerResponse object
        """
        card_issuer_response = CardIssuerResponse()
        card_issuer_response.result = card_provider.get("result")
        card_issuer_response.avs_result = card_provider.get("avs_result")
        card_issuer_response.cvv_result = card_provider.get("cvv_result")
        card_issuer_response.avs_address_result = card_provider.get(
            "avs_address_result"
        )
        card_issuer_response.avs_postal_code_result = card_provider.get(
            "avs_postal_code_result"
        )

        return card_issuer_response

    @staticmethod
    def _map_address_object(
        address: Optional[Dict[str, Any]], address_type: Optional[AddressType] = None
    ) -> Address:
        """
        Maps address data to Address object

        @param address: Address data
        @param address_type: Type of address
        @return: Mapped Address object
        """
        if not address:
            return Address()

        user_address = Address()
        user_address.type = address_type
        user_address.street_address1 = address.get("line_1")
        user_address.street_address2 = address.get("line_2")
        user_address.street_address3 = address.get("line_3")
        user_address.city = address.get("city")
        user_address.state = address.get("state")
        user_address.postal_code = address.get("postal_code")
        user_address.country_code = address.get("country")

        functions = address.get("functions", [])
        if functions and len(functions) > 0:
            user_address.type = functions[0]
        else:
            user_address.type = address_type

        return user_address

    @staticmethod
    def map_report_response(response: Dict[str, Any], report_type: ReportType) -> Union[
        TransactionSummary,
        PagedResult,
        StoredPaymentMethodSummary,
        DepositSummary,
        DisputeSummary,
        DisputeDocument,
    ]:
        """
        Maps report response to appropriate entity

        @param response: Report response
        @param report_type: Type of report
        @return: Mapped entity object
        """
        if report_type == ReportType.TransactionDetail:
            return GpApiMapping.map_transaction_summary(response)

        elif report_type == ReportType.FindStoredPaymentMethodsPaged:
            report = GpApiMapping._set_paging_info(response)
            if response.get("payment_methods"):
                for spm in response.get("payment_methods", []):
                    report.result.append(
                        GpApiMapping.map_stored_payment_method_summary(spm)
                    )
            return report

        elif report_type == ReportType.StoredPaymentMethodDetail:
            return GpApiMapping.map_stored_payment_method_summary(response)

        elif report_type in (
            ReportType.FindTransactionsPaged,
            ReportType.FindSettlementTransactionsPaged,
        ):
            report = GpApiMapping._set_paging_info(response)
            report.result = [
                GpApiMapping.map_transaction_summary(transaction)
                for transaction in response.get("transactions", [])
            ]
            return report

        elif report_type == ReportType.DepositDetail:
            return GpApiMapping._map_deposit_summary(response)

        elif report_type == ReportType.FindDepositsPaged:
            report = GpApiMapping._set_paging_info(response)
            report.result = [
                GpApiMapping._map_deposit_summary(deposit)
                for deposit in response.get("deposits", [])
            ]
            return report

        elif report_type in (
            ReportType.DisputeDetail,
            ReportType.SettlementDisputeDetail,
        ):
            return GpApiMapping._map_dispute_summary(response)

        elif report_type == ReportType.DocumentDisputeDetail:
            report = DisputeDocument()
            report.id = response.get("id")
            report.b64_content = response.get("b64_content")
            return report

        elif report_type in (
            ReportType.FindDisputesPaged,
            ReportType.FindSettlementDisputesPaged,
        ):
            report = GpApiMapping._set_paging_info(response)
            report.result = [
                GpApiMapping._map_dispute_summary(dispute)
                for dispute in response.get("disputes", [])
            ]
            return report

        raise ApiException("Report type not supported!")

    @staticmethod
    def map_transaction_summary(response: Dict[str, Any]) -> TransactionSummary:
        """
        Maps response to TransactionSummary

        @param response: Response data
        @return: Mapped TransactionSummary object
        """
        summary = GpApiMapping._create_transaction_summary(response)

        if response.get("time_created_reference"):
            # Store as string instead of datetime to fix the type error
            time_created = response.get("time_created_reference", "").replace(
                "Z", "+00:00"
            )
            summary.transaction_local_date = time_created

        summary.batch_sequence_number = response.get("batch_id")
        summary.country = response.get("country")
        summary.original_transaction_id = response.get("parent_resource_id")
        summary.deposit_reference = response.get("deposit_id", "")
        summary.deposit_status = response.get("deposit_status", "")

        if response.get("deposit_time_created"):
            # Store as string instead of datetime to fix the type error
            deposit_time = response.get("deposit_time_created", "").replace(
                "Z", "+00:00"
            )
            summary.deposit_time_created = deposit_time

        summary.order_id = response.get("order_reference")

        if response.get("system"):
            GpApiMapping._map_system_response(summary, response.get("system", {}))

        if response.get("payment_method"):
            payment_method = response.get("payment_method", {})
            card = payment_method.get("card", {})

            summary.gateway_response_message = payment_method.get("message")
            summary.entry_mode = payment_method.get("entry_mode")
            summary.card_holder_name = payment_method.get("name", "")

            if payment_method.get("card"):
                card = payment_method.get("card", {})
                summary.aquirer_reference_number = card.get("arn")
                summary.masked_card_number = card.get("masked_number_first6last4")
                summary.payment_type = PaymentMethodName.CARD

            elif payment_method.get("digital_wallet"):
                digital_wallet = payment_method.get("digital_wallet", {})
                summary.masked_card_number = digital_wallet.get(
                    "masked_token_first6last4"
                )
                summary.payment_type = PaymentMethodName.DIGITAL_WALLET

            elif payment_method.get("bank_transfer") and not payment_method.get("apm"):
                summary.payment_type = PaymentMethodName.BANK_TRANSFER
                bank_transfer = payment_method.get("bank_transfer", {})
                summary.account_number_last4 = bank_transfer.get(
                    "masked_account_number_last4"
                )
                summary.account_type = bank_transfer.get("account_type")

            if payment_method.get("card"):
                summary.card_type = card.get("brand")
                summary.auth_code = card.get("authcode")
                summary.brand_reference = card.get("brand_reference")

            if payment_method.get("apm"):
                # Map Open Banking response info
                if (
                    payment_method.get("apm", {}).get("provider", "").lower()
                    == PaymentProvider.OPEN_BANKING.value.lower()
                ):
                    # To be implemented
                    pass
                else:
                    # Map APMs (Paypal) response info
                    apm = payment_method.get("apm", {})
                    alternative_payment_response = AlternativePaymentResponse()
                    alternative_payment_response.redirect_url = payment_method.get(
                        "redirect_url"
                    )
                    alternative_payment_response.provider_name = apm.get("provider")
                    alternative_payment_response.provider_reference = apm.get(
                        "provider_reference"
                    )
                    summary.alternative_payment_response = alternative_payment_response
                    summary.payment_type = PaymentMethodName.APM

        return summary

    @staticmethod
    def _create_transaction_summary(response: Dict[str, Any]) -> TransactionSummary:
        """
        Creates and initializes a new TransactionSummary

        @param response: Response data
        @return: New TransactionSummary object
        """
        transaction = TransactionSummary()
        transaction.transaction_id = response.get("id")

        time_created = GpApiMapping._validate_string_date(
            response.get("time_created", "")
        )
        if time_created:
            transaction.transaction_date = time_created.replace("Z", "+00:00")

        transaction.transaction_status = response.get("status")
        transaction.transaction_type = response.get("type")
        transaction.channel = response.get("channel")
        transaction.amount = StringUtils.to_amount(response.get("amount"))
        transaction.currency = response.get("currency")
        transaction.reference_number = transaction.client_transaction_id = response.get(
            "reference"
        )
        transaction.description = response.get("description")
        transaction.fingerprint = response.get("payment_method", {}).get("fingerprint")
        transaction.fingerprint_indicator = response.get("payment_method", {}).get(
            "fingerprint_presence_indicator"
        )

        return transaction

    @staticmethod
    def _validate_string_date(date: str) -> str:
        """
        Validates a date string

        @param date: Date string to validate
        @return: Valid date string or empty string
        """
        try:
            datetime.fromisoformat(date.replace("Z", "+00:00"))
            return date
        except (ValueError, TypeError):
            return ""

    @staticmethod
    def _map_system_response(
        summary: Union[TransactionSummary, DepositSummary], system: Dict[str, Any]
    ) -> None:
        """
        Maps system data to summary object

        @param summary: Summary object to update
        @param system: System data
        """
        if not system:
            return

        summary.merchant_id = system.get("mid")
        summary.merchant_hierarchy = system.get("hierarchy")
        summary.merchant_name = system.get("name")
        summary.merchant_dba_name = system.get("dba")

    @staticmethod
    def map_stored_payment_method_summary(
        response: Dict[str, Any]
    ) -> StoredPaymentMethodSummary:
        """
        Maps response to StoredPaymentMethodSummary

        @param response: Response data
        @return: Mapped StoredPaymentMethodSummary object
        """
        summary = StoredPaymentMethodSummary()
        summary.payment_method_id = response.get("id")

        if response.get("time_created"):
            summary.time_created = datetime.fromisoformat(
                response.get("time_created", "").replace("Z", "+00:00")
            )

        summary.status = response.get("status", "")
        summary.reference = response.get("reference", "")
        summary.card_holder_name = response.get("name", "")

        if response.get("card"):
            card = response.get("card", {})
            summary.card_type = card.get("brand", "")
            summary.card_number_last_four = card.get("number_last4", "")
            summary.card_exp_month = int(card.get("expiry_month", 0)) or None
            summary.card_exp_year = int(card.get("expiry_year", 0)) or None

        return summary

    @staticmethod
    def _set_paging_info(response: Dict[str, Any]) -> PagedResult:
        """
        Sets paging information in PagedResult

        @param response: Response with paging data
        @return: PagedResult with paging info set
        """
        page_info = PagedResult()

        page_info.total_record_count = (
            response.get("total_count")
            if response.get("total_count") is not None
            else (
                response.get("total_record_count")
                if response.get("total_record_count") is not None
                else None
            )
        )

        paging = response.get("paging", {})
        page_info.page_size = paging.get("page_size")
        page_info.page = paging.get("page")
        page_info.order = paging.get("order")
        page_info.order_by = paging.get("order_by")

        return page_info

    @staticmethod
    def map_response_secure3D(response: Dict[str, Any]) -> Transaction:
        """
        Maps response to 3DS Transaction object

        @param response: 3DS response data
        @return: Mapped Transaction with 3DS data
        """
        transaction = Transaction()
        three_d_secure = ThreeDSecure()
        three_d_secure.server_transaction_id = response.get("id")

        if response.get("three_ds") and response.get("three_ds", {}).get(
            "message_version"
        ):
            message_version = response.get("three_ds", {}).get("message_version", "")
            version = ThreeDSecureVersion.Any

            if message_version.startswith("1."):
                version = ThreeDSecureVersion.One
            elif message_version.startswith("2."):
                version = ThreeDSecureVersion.Two

            three_d_secure.message_version = message_version
            three_d_secure.version = version

        three_d_secure.status = response.get("status")
        three_d_secure.directory_server_start_version = response.get(
            "three_ds", {}
        ).get("ds_protocol_version_start")
        three_d_secure.directory_server_end_version = response.get("three_ds", {}).get(
            "ds_protocol_version_end"
        )
        three_d_secure.acs_start_version = response.get("three_ds", {}).get(
            "acs_protocol_version_start"
        )
        three_d_secure.acs_end_version = response.get("three_ds", {}).get(
            "acs_protocol_version_end"
        )
        three_d_secure.enrolled = response.get("three_ds", {}).get("enrolled_status")
        three_d_secure.eci = response.get("three_ds", {}).get("eci")
        three_d_secure.acs_info_indicator = response.get("three_ds", {}).get(
            "acs_info_indicator"
        )
        three_d_secure.acs_reference_number = response.get("three_ds", {}).get(
            "acs_reference_number"
        )
        three_d_secure.provider_server_trans_ref = response.get("three_ds", {}).get(
            "server_trans_ref"
        )
        three_d_secure.challenge_mandated = (
            response.get("three_ds", {}).get("challenge_status") == "MANDATED"
        )
        three_d_secure.payer_authentication_request = (
            response.get("three_ds", {})
            .get("method_data", {})
            .get("encoded_method_data")
        )
        three_d_secure.issuer_acs_url = response.get("three_ds", {}).get("method_url")
        three_d_secure.authentication_source = response.get("three_ds", {}).get(
            "authentication_source"
        )

        three_ds = response.get("three_ds", {})
        if (
            three_ds.get("acs_challenge_request_url")
            and three_d_secure.status == Secure3dStatus.CHALLENGE_REQUIRED.value
        ):
            three_d_secure.issuer_acs_url = three_ds.get("acs_challenge_request_url")
            three_d_secure.payer_authentication_request = three_ds.get(
                "challenge_value"
            )

        if (
            three_d_secure.authentication_source == AuthenticationSource.MobileSdk
            and three_ds.get("mobile_data")
        ):
            mobile_data = three_ds.get("mobile_data", {})
            three_d_secure.payer_authentication_request = mobile_data.get(
                "acs_signed_content"
            )
            three_d_secure.acs_interface = mobile_data.get(
                "acs_rendering_type", {}
            ).get("acs_interface")
            three_d_secure.acs_ui_template = mobile_data.get(
                "acs_rendering_type", {}
            ).get("acs_ui_template")

        three_d_secure.currency = response.get("currency")
        three_d_secure.amount = StringUtils.to_amount(response.get("amount"))
        three_d_secure.authentication_value = three_ds.get("authentication_value")
        three_d_secure.directory_server_transaction_id = three_ds.get("ds_trans_ref")
        three_d_secure.acs_transaction_id = three_ds.get("acs_trans_ref")
        three_d_secure.status_reason = three_ds.get("status_reason")
        three_d_secure.message_category = three_ds.get("message_category")
        three_d_secure.message_type = three_ds.get("message_type")
        three_d_secure.session_data_field_name = three_ds.get("session_data_field_name")
        three_d_secure.challenge_return_url = response.get("notifications", {}).get(
            "challenge_return_url"
        )
        three_d_secure.liability_shift = three_ds.get("liability_shift")
        three_d_secure.authentication_type = three_ds.get("authentication_request_type")
        three_d_secure.decoupled_response_indicator = three_ds.get(
            "acs_decoupled_response_indicator"
        )
        three_d_secure.whitelist_status = three_ds.get("whitelist_status")

        if three_ds.get("message_extension"):
            for message_extension in three_ds.get("message_extension", []):
                msg_item = MessageExtension()
                msg_item.criticality_indicator = message_extension.get(
                    "criticality_indicator"
                )
                msg_item.message_extension_data = (
                    json.dumps(message_extension.get("data"))
                    if message_extension.get("data")
                    else ""
                )
                msg_item.message_extension_id = message_extension.get("id")
                msg_item.message_extension_name = message_extension.get("name")
                three_d_secure.message_extension.append(msg_item)

        transaction.three_d_secure = three_d_secure

        return transaction

    @staticmethod
    def map_response_apm(response: Dict[str, Any]) -> Transaction:
        """
        Maps API response to Transaction object with Alternative Payment Method details

        @param response: The API response
        @return: Mapped Transaction object with APM details
        """
        apm = AlternativePaymentResponse()
        transaction = GpApiMapping.map_response(response)
        payment_method_apm = response.get("payment_method", {}).get("apm", {})

        apm.redirect_url = response.get("payment_method", {}).get(
            "redirect_url"
        ) or payment_method_apm.get("redirect_url")
        apm.qr_code_image = response.get("payment_method", {}).get("qr_code")

        if isinstance(payment_method_apm.get("provider"), str):
            apm.provider_name = payment_method_apm.get("provider")
        elif isinstance(payment_method_apm.get("provider"), dict):
            provider = payment_method_apm.get("provider", {})
            apm.provider_name = provider.get("name")
            apm.provider_reference = provider.get("merchant_identifier")
            apm.time_created_reference = provider.get("time_created_reference")

        apm.account_holder_name = payment_method_apm.get("provider_payer_name")
        apm.ack = payment_method_apm.get("ack")
        apm.session_token = payment_method_apm.get("session_token")
        apm.correlation_reference = payment_method_apm.get("correlation_reference")
        apm.version_reference = payment_method_apm.get("version_reference")
        apm.build_reference = payment_method_apm.get("build_reference")
        apm.time_created_reference = payment_method_apm.get("time_created_reference")
        apm.transaction_reference = payment_method_apm.get("transaction_reference")
        apm.secure_account_reference = payment_method_apm.get(
            "secure_account_reference"
        )
        apm.reason_code = payment_method_apm.get("reason_code")
        apm.pending_reason = payment_method_apm.get("pending_reason")
        apm.gross_amount = StringUtils.to_amount(payment_method_apm.get("gross_amount"))
        apm.payment_time_reference = payment_method_apm.get("payment_time_reference")
        apm.payment_type = payment_method_apm.get("payment_type")
        apm.payment_status = payment_method_apm.get("payment_status")
        apm.type = payment_method_apm.get("type")
        apm.protection_eligibilty = payment_method_apm.get("protection_eligibilty")
        apm.fee_amount = StringUtils.to_amount(payment_method_apm.get("fee_amount"))

        if response.get("payment_method", {}).get("authorization"):
            authorization = response.get("payment_method", {}).get("authorization", {})
            apm.auth_status = authorization.get("status")
            apm.auth_amount = StringUtils.to_amount(authorization.get("amount"))
            apm.auth_ack = authorization.get("ack")
            apm.auth_correlation_reference = authorization.get("correlation_reference")
            apm.auth_version_reference = authorization.get("version_reference")
            apm.auth_build_reference = authorization.get("build_reference")
            apm.auth_pending_reason = authorization.get("pending_reason")
            apm.auth_protection_eligibilty = authorization.get("protection_eligibilty")
            apm.auth_protection_eligibilty_type = authorization.get(
                "protection_eligibilty_type"
            )
            apm.auth_reference = authorization.get("reference")

        apm.next_action = payment_method_apm.get("next_action")
        apm.seconds_to_expire = payment_method_apm.get("seconds_to_expire")
        transaction.alternative_payment_response = apm

        return transaction

    @staticmethod
    def _map_deposit_summary(response: Dict[str, Any]) -> DepositSummary:
        """
        Maps response to DepositSummary

        @param response: Deposit response data
        @return: Mapped DepositSummary object
        """
        summary = DepositSummary()
        summary.deposit_id = response.get("id")

        if response.get("time_created"):
            summary.deposit_date = datetime.fromisoformat(
                response.get("time_created", "").replace("Z", "+00:00")
            )

        summary.status = response.get("status")
        summary.type = response.get("funding_type")
        summary.amount = StringUtils.to_amount(response.get("amount"))
        summary.currency = response.get("currency")

        if response.get("system"):
            GpApiMapping._map_system_response(summary, response.get("system", {}))

        if response.get("sales"):
            sales = response.get("sales", {})
            summary.sales_total_count = sales.get("count", 0)
            summary.sales_total_amount = StringUtils.to_amount(sales.get("amount"))

        if response.get("refunds"):
            refunds = response.get("refunds", {})
            summary.refunds_total_count = refunds.get("count", 0)
            summary.refunds_total_amount = StringUtils.to_amount(refunds.get("amount"))

        if response.get("disputes"):
            disputes = response.get("disputes", {})
            summary.chargeback_total_count = disputes.get("chargebacks", {}).get(
                "count", 0
            )
            summary.chargeback_total_amount = StringUtils.to_amount(
                disputes.get("chargebacks", {}).get("amount")
            )

            summary.adjustment_total_count = disputes.get("reversals", {}).get(
                "count", 0
            )
            summary.adjustment_total_amount = StringUtils.to_amount(
                disputes.get("reversals", {}).get("amount")
            )

        summary.fees_total_amount = StringUtils.to_amount(
            response.get("fees", {}).get("amount")
        )

        return summary

    @staticmethod
    def _map_dispute_summary(response: Dict[str, Any]) -> DisputeSummary:
        """
        Maps response to DisputeSummary

        @param response: Dispute response data
        @return: Mapped DisputeSummary object
        """
        summary = DisputeSummary()
        summary.case_id = response.get("id")

        if response.get("time_created"):
            summary.case_id_time = datetime.fromisoformat(
                response.get("time_created", "").replace("Z", "+00:00")
            )
        elif response.get("stage_time_created"):
            summary.case_id_time = datetime.fromisoformat(
                response.get("stage_time_created", "").replace("Z", "+00:00")
            )

        summary.case_status = response.get("status")
        summary.case_stage = response.get("stage")
        summary.case_amount = StringUtils.to_amount(response.get("amount"))
        summary.case_currency = response.get("currency")

        if response.get("system"):
            system = response.get("system", {})
            summary.case_merchant_id = system.get("mid")
            summary.merchant_hierarchy = system.get("hierarchy")
            summary.merchant_name = system.get("name")

        card = response.get("transaction", {}).get("payment_method", {}).get(
            "card", {}
        ) or response.get("payment_method", {}).get("card", {})

        if card:
            summary.transaction_arn = card.get("arn")
            summary.transaction_card_type = card.get("brand")
            summary.transaction_masked_card_number = card.get("number")

        if response.get("transaction"):
            transaction = response.get("transaction", {})

            if transaction.get("time_created"):
                summary.transaction_time = datetime.fromisoformat(
                    transaction.get("time_created", "").replace("Z", "+00:00")
                )

            summary.transaction_type = transaction.get("type")
            summary.transaction_amount = StringUtils.to_amount(
                transaction.get("amount")
            )
            summary.transaction_currency = transaction.get("currency")
            summary.transaction_reference_number = transaction.get("reference")

            if transaction.get("payment_method", {}).get("card"):
                card = transaction.get("payment_method", {}).get("card", {})
                summary.transaction_masked_card_number = card.get(
                    "masked_number_first6last4", ""
                )
                summary.transaction_auth_code = card.get("authcode")

        if response.get("documents"):
            summary.documents = []
            for document in response.get("documents", []):
                if document.get("id"):
                    dispute_document = DisputeDocument()
                    dispute_document.id = document.get("id")
                    dispute_document.type = document.get("type")
                    summary.documents.append(dispute_document)
        return summary

    @staticmethod
    def _map_dcc_info(response: Dict[str, Any]) -> DccRateData:
        """
        Maps DCC (Dynamic Currency Conversion) information

        @param response: Response containing DCC data
        @return: Mapped DccRateData object
        """
        if response.get("currency_conversion"):
            response = response.get("currency_conversion", {})

        dcc_rate_data = DccRateData()
        dcc_rate_data.card_holder_currency = response.get("payer_currency")
        dcc_rate_data.card_holder_amount = StringUtils.to_amount(
            response.get("payer_amount")
        )
        dcc_rate_data.card_holder_rate = response.get("exchange_rate")
        dcc_rate_data.merchant_currency = response.get("currency")
        dcc_rate_data.merchant_amount = StringUtils.to_amount(response.get("amount"))
        dcc_rate_data.margin_rate_percentage = response.get("margin_rate_percentage")
        dcc_rate_data.exchange_rate_source_name = response.get("exchange_rate_source")
        dcc_rate_data.commission_percentage = response.get("commission_percentage")
        dcc_rate_data.exchange_rate_source_timestamp = response.get(
            "exchange_rate_time_created"
        )
        dcc_rate_data.dcc_id = response.get("id")

        return dcc_rate_data
