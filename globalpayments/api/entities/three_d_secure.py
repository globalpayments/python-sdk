from dataclasses import dataclass, field
from typing import Optional, Union, List

from globalpayments.api.entities.enums import (
    ThreeDSecureVersion,
    AuthenticationSource,
    ExemptStatus,
    ExemptionReason,
)
from globalpayments.api.entities.merchant_data_collection import MerchantDataCollection
from globalpayments.api.entities.message_extension import MessageExtension


@dataclass
class ThreeDSecure(object):
    enrolled: Optional[str] = field(default=None)
    payer_authentication_response: Optional[str] = field(default=None)
    issuer_acs_url: Optional[str] = field(default=None)
    authentication_source: Optional[AuthenticationSource] = field(default=None)
    status: Optional[str] = field(default=None)
    eci: Optional[Union[str, int]] = field(default=None)
    xid: Optional[str] = field(default=None)
    cavv: Optional[str] = field(default=None)
    version: ThreeDSecureVersion = field(default=ThreeDSecureVersion.Two)
    algorithm: Optional[str] = field(default=None)
    currency: Optional[str] = field(default=None)
    amount: Optional[str] = field(default=None)
    exempt_status: Optional[ExemptStatus] = field(default=None)
    message_category: Optional[str] = field(default=None)
    message_version: Optional[str] = field(default=None)
    message_type: Optional[str] = field(default=None)
    server_transaction_id: Optional[str] = field(default=None)
    message_extension: Optional[List[MessageExtension]] = field(default=None)
    merchant_data: Optional[MerchantDataCollection] = field(default=None)
    order_id: Optional[str] = field(default=None)
    acs_transaction_id: Optional[str] = field(default=None)
    acs_end_version: Optional[str] = field(default=None)
    acs_start_version: Optional[str] = field(default=None)
    acs_info_indicator: Optional[str] = field(default=None)
    acs_interface: Optional[str] = field(default=None)
    acs_ui_template: Optional[str] = field(default=None)
    authentication_type: Optional[str] = field(default=None)
    authentication_value: Optional[str] = field(default=None)
    challenge_mandated: Optional[bool] = field(default=None)
    challenge_return_url: Optional[str] = field(default=None)
    decoupled_response_indicator: Optional[str] = field(default=None)
    directory_server_transaction_id: Optional[str] = field(default=None)
    directory_server_end_version: Optional[str] = field(default=None)
    directory_server_start_version: Optional[str] = field(default=None)
    liability_shift: Optional[str] = field(default=None)
    payer_authentication_request: Optional[str] = field(default=None)
    status_reason: Optional[str] = field(default=None)
    session_data_field_name: Optional[str] = field(default=None)
    whitelist_status: Optional[str] = field(default=None)
    acs_reference_number: Optional[str] = field(default=None)
    provider_server_trans_ref: Optional[str] = field(default=None)

    card_holder_response_info: Optional[str] = field(default=None)
    payment_data_source: Optional[str] = field(default=None)
    payment_data_type: Optional[str] = field(default="3DSecure")
    sdk_interface: Optional[str] = field(default=None)
    sdk_ui_type: Optional[str] = field(default=None)
    secure_code: Optional[str] = field(default=None)
    exempt_reason: Optional[ExemptionReason] = field(default=None)

    def get_merchant_data(self):
        if not hasattr(self, "merchant_data") or self.merchant_data is None:
            self.merchant_data = MerchantDataCollection()
        return self.merchant_data

    def set_merchant_data(self, merchant_data):
        if hasattr(self, "merchant_data") and self.merchant_data is not None:
            self.merchant_data.merge_hidden(merchant_data)

        self.merchant_data = merchant_data

        if self.merchant_data.has_key("amount"):
            self.amount = self.merchant_data.get_value("amount")

        if self.merchant_data.has_key("currency"):
            self.currency = self.merchant_data.get_value("currency")

        if self.merchant_data.has_key("orderId"):
            self.order_id = self.merchant_data.get_value("orderId")

        if self.merchant_data.has_key("version"):
            self.version = self.merchant_data.get_value("version")

    def merge(self, secure_ecom):
        if secure_ecom:

            self.enrolled = self._merge_value(self.enrolled, secure_ecom.enrolled)
            self.issuer_acs_url = self._merge_value(
                self.issuer_acs_url, secure_ecom.issuer_acs_url
            )
            self.authentication_source = self._merge_value(
                self.authentication_source, secure_ecom.authentication_source
            )
            self.status = self._merge_value(self.status, secure_ecom.status)
            self.eci = self._merge_value(self.eci, secure_ecom.eci)
            self.xid = self._merge_value(self.xid, secure_ecom.xid)
            self.cavv = self._merge_value(self.cavv, secure_ecom.cavv)
            self.version = self._merge_value(self.version, secure_ecom.version)
            self.algorithm = self._merge_value(self.algorithm, secure_ecom.algorithm)
            self.currency = self._merge_value(self.currency, secure_ecom.currency)
            self.amount = self._merge_value(self.amount, secure_ecom.amount)
            self.message_category = self._merge_value(
                self.message_category, secure_ecom.message_category
            )
            self.message_version = self._merge_value(
                self.message_version, secure_ecom.message_version
            )
            self.message_type = self._merge_value(
                self.message_type, secure_ecom.message_type
            )
            self.message_extension = self._merge_value(
                self.message_extension, secure_ecom.message_extension
            )
            self.server_transaction_id = self._merge_value(
                self.server_transaction_id, secure_ecom.server_transaction_id
            )

            self.acs_transaction_id = self._merge_value(
                self.acs_transaction_id, secure_ecom.acs_transaction_id
            )
            self.acs_end_version = self._merge_value(
                self.acs_end_version, secure_ecom.acs_end_version
            )
            self.acs_start_version = self._merge_value(
                self.acs_start_version, secure_ecom.acs_start_version
            )
            self.acs_interface = self._merge_value(
                self.acs_interface, secure_ecom.acs_interface
            )
            self.acs_ui_template = self._merge_value(
                self.acs_ui_template, secure_ecom.acs_ui_template
            )
            self.authentication_type = self._merge_value(
                self.authentication_type, secure_ecom.authentication_type
            )
            self.authentication_value = self._merge_value(
                self.authentication_value, secure_ecom.authentication_value
            )
            self.challenge_mandated = self._merge_value(
                self.challenge_mandated, secure_ecom.challenge_mandated
            )
            self.decoupled_response_indicator = self._merge_value(
                self.decoupled_response_indicator,
                secure_ecom.decoupled_response_indicator,
            )
            self.directory_server_transaction_id = self._merge_value(
                self.directory_server_transaction_id,
                secure_ecom.directory_server_transaction_id,
            )
            self.directory_server_end_version = self._merge_value(
                self.directory_server_end_version,
                secure_ecom.directory_server_end_version,
            )
            self.directory_server_start_version = self._merge_value(
                self.directory_server_start_version,
                secure_ecom.directory_server_start_version,
            )
            self.order_id = self._merge_value(self.order_id, secure_ecom.order_id)
            self.payer_authentication_request = self._merge_value(
                self.payer_authentication_request,
                secure_ecom.payer_authentication_request,
            )
            self.status_reason = self._merge_value(
                self.status_reason, secure_ecom.status_reason
            )
            self.whitelist_status = self._merge_value(
                self.whitelist_status, secure_ecom.whitelist_status
            )
            self.session_data_field_name = self._merge_value(
                self.session_data_field_name, secure_ecom.session_data_field_name
            )
            self.challenge_return_url = self._merge_value(
                self.challenge_return_url, secure_ecom.challenge_return_url
            )
            self.liability_shift = self._merge_value(
                self.liability_shift, secure_ecom.liability_shift
            )
            self.acs_reference_number = self._merge_value(
                self.acs_reference_number, secure_ecom.acs_reference_number
            )
            self.provider_server_trans_ref = self._merge_value(
                self.provider_server_trans_ref, secure_ecom.provider_server_trans_ref
            )

            self.card_holder_response_info = self._merge_value(
                self.card_holder_response_info, secure_ecom.card_holder_response_info
            )
            self.payment_data_source = self._merge_value(
                self.payment_data_source, secure_ecom.payment_data_source
            )
            self.payment_data_type = self._merge_value(
                self.payment_data_type, secure_ecom.payment_data_type
            )
            self.sdk_interface = self._merge_value(
                self.sdk_interface, secure_ecom.sdk_interface
            )
            self.sdk_ui_type = self._merge_value(
                self.sdk_ui_type, secure_ecom.sdk_ui_type
            )
            self.secure_code = self._merge_value(
                self.secure_code, secure_ecom.secure_code
            )
            self.exempt_reason = self._merge_value(
                self.exempt_reason, secure_ecom.exempt_reason
            )

            # Merchant data merge
            if hasattr(self, "merchant_data") and hasattr(secure_ecom, "merchant_data"):
                self.merchant_data = self._merge_value(
                    self.merchant_data, secure_ecom.merchant_data
                )

    def _merge_value(self, current_value, merge_value):
        """
        Helper method to merge values.
        Returns the merge_value if it's not None, otherwise keeps the current_value.
        """
        return merge_value if merge_value is not None else current_value
