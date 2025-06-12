"""
Report request builder for Global Payments API
"""

from datetime import datetime as dt
from enum import Enum
from typing import Any

from globalpayments.api.builders.request_builder.IRequestBuilder import IRequestBuilder
from globalpayments.api.entities.enums import HttpVerb, ReportType, SearchCriteria
from globalpayments.api.entities.gp_api.gp_api_request import GpApiRequest
from globalpayments.api.payment_methods import CreditCardData
from globalpayments.api.utils import StringUtils
from globalpayments.api.utils.serializer import object_serialize


class GpApiReportRequestBuilder(IRequestBuilder):
    """
    Builds report requests for the Global Payments API
    """

    def __init__(self):
        """
        Initialize the report request builder
        """
        pass

    def can_process(self, builder: Any) -> bool:
        """
        Determines if this builder can process the provided builder

        Args:
            builder: The builder to check

        Returns:
            True if this builder can process the provided builder, otherwise False
        """
        from globalpayments.api.builders import ReportBuilder

        return isinstance(builder, ReportBuilder)

    def build_request(self, builder: Any, config: Any = None) -> GpApiRequest:
        """
        Builds a request from the provided builder

        Args:
            builder: The report builder
            config: The GP API configuration

        Returns:
            A GpApiRequest object
        """
        query_params = {}
        endpoint = ""
        verb = HttpVerb.GET
        payload = None

        # Add basic params
        if hasattr(builder, "time_zone_conversion") and builder.time_zone_conversion:
            query_params["zone"] = builder.time_zone_conversion

        if hasattr(builder, "page") and builder.page:
            query_params["page"] = builder.page

        if hasattr(builder, "page_size") and builder.page_size:
            query_params["page_size"] = builder.page_size

        # Match reportType structure
        if builder.report_type == ReportType.TransactionDetail:
            endpoint = f"{GpApiRequest.TRANSACTION_ENDPOINT}/{builder.transaction_id}"
            verb = HttpVerb.GET

        elif builder.report_type == ReportType.FindStoredPaymentMethodsPaged:
            # Handle credit card search case
            if (
                hasattr(builder, "search_builder")
                and hasattr(builder.search_builder, "payment_method")
                and isinstance(builder.search_builder.payment_method, CreditCardData)
            ):

                endpoint = f"{GpApiRequest.PAYMENT_METHODS_ENDPOINT}/search"
                verb = HttpVerb.POST

                payment_method = builder.search_builder.payment_method
                card = {
                    "number": payment_method.number,
                    "expiry_month": (
                        str(payment_method.exp_month).zfill(2)
                        if payment_method.exp_month
                        else None
                    ),
                    "expiry_year": (
                        str(payment_method.exp_year).zfill(4)[-2:]
                        if payment_method.exp_year
                        else None
                    ),
                }

                payload = {
                    "account_name": config.access_token_info.tokenization_account_name,
                    "account_id": config.access_token_info.tokenization_account_id,
                    "reference": (
                        builder.search_builder.reference_number
                        if hasattr(builder.search_builder, "reference_number")
                        else None
                    ),
                    "card": card,
                }
            else:
                endpoint = GpApiRequest.PAYMENT_METHODS_ENDPOINT
                verb = HttpVerb.GET

                from_time_last_updated = ""
                if hasattr(builder, "search_builder") and hasattr(
                    builder.search_builder, "from_time_last_updated"
                ):
                    from_time_last_updated = (
                        builder.search_builder.from_time_last_updated
                    )

                to_time_last_updated = ""
                if hasattr(builder, "search_builder") and hasattr(
                    builder.search_builder, "to_time_last_updated"
                ):
                    to_time_last_updated = builder.search_builder.to_time_last_updated

                query_params.update(
                    {
                        "order_by": (
                            builder.stored_payment_method_order_by
                            if hasattr(builder, "stored_payment_method_order_by")
                            else None
                        ),
                        "order": builder.order if hasattr(builder, "order") else None,
                        "number_last4": (
                            getattr(
                                builder.search_builder,
                                SearchCriteria.CardNumberLastFour.value,
                                None,
                            )
                            if hasattr(builder, "search_builder")
                            else None
                        ),
                        "reference": (
                            getattr(
                                builder.search_builder,
                                SearchCriteria.ReferenceNumber.value,
                                None,
                            )
                            if hasattr(builder, "search_builder")
                            else None
                        ),
                        "status": (
                            getattr(
                                builder.search_builder,
                                SearchCriteria.StoredPaymentMethodStatus.value,
                                None,
                            )
                            if hasattr(builder, "search_builder")
                            else None
                        ),
                        "from_time_created": (
                            getattr(
                                builder.search_builder,
                                SearchCriteria.StartDate.value,
                                None,
                            )
                            if hasattr(builder, "search_builder")
                            else None
                        ),
                        "to_time_created": (
                            getattr(
                                builder.search_builder,
                                SearchCriteria.EndDate.value,
                                None,
                            )
                            if hasattr(builder, "search_builder")
                            else None
                        ),
                        "from_time_last_updated": from_time_last_updated or None,
                        "to_time_last_updated": to_time_last_updated or None,
                        "id": (
                            getattr(
                                builder.search_builder,
                                SearchCriteria.StoredPaymentMethodId.value,
                                None,
                            )
                            if hasattr(builder, "search_builder")
                            else None
                        ),
                    }
                )

        elif builder.report_type == ReportType.StoredPaymentMethodDetail:
            endpoint = f"{GpApiRequest.PAYMENT_METHODS_ENDPOINT}/{getattr(builder.search_builder, SearchCriteria.StoredPaymentMethodId.value)}"
            verb = HttpVerb.GET

        elif builder.report_type == ReportType.FindTransactionsPaged:
            endpoint = GpApiRequest.TRANSACTION_ENDPOINT
            verb = HttpVerb.GET

            query_params.update(
                {
                    "id": (
                        builder.transaction_id
                        if hasattr(builder, "transaction_id")
                        else None
                    ),
                    "type": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.PaymentType.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "channel": (
                        getattr(
                            builder.search_builder, SearchCriteria.Channel.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "amount": (
                        StringUtils.to_numeric(
                            getattr(
                                builder.search_builder,
                                SearchCriteria.Amount.value,
                                None,
                            )
                        )
                        if (
                            hasattr(builder, "search_builder")
                            and hasattr(
                                builder.search_builder, SearchCriteria.Amount.value
                            )
                        )
                        else None
                    ),
                    "currency": (
                        getattr(
                            builder.search_builder, SearchCriteria.Currency.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "number_first6": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.CardNumberFirstSix.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "number_last4": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.CardNumberLastFour.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "token_first6": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.TokenFirstSix.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "token_last4": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.TokenLastFour.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "account_name": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.AccountName.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "brand": (
                        getattr(
                            builder.search_builder, SearchCriteria.CardBrand.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "brand_reference": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.BrandReference.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "authcode": (
                        getattr(
                            builder.search_builder, SearchCriteria.AuthCode.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "reference": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.ReferenceNumber.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "status": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.TransactionStatus.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "from_time_created": (
                        getattr(
                            builder.search_builder, SearchCriteria.StartDate.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "to_time_created": (
                        getattr(
                            builder.search_builder, SearchCriteria.EndDate.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "country": (
                        getattr(
                            builder.search_builder, SearchCriteria.Country.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "batch_id": (
                        getattr(
                            builder.search_builder, SearchCriteria.BatchId.value, None
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "entry_mode": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.PaymentEntryMode.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "name": (
                        getattr(builder.search_builder, SearchCriteria.Name.value, None)
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                    "payment_method": (
                        getattr(
                            builder.search_builder,
                            SearchCriteria.PaymentMethodName.value,
                            None,
                        )
                        if hasattr(builder, "search_builder")
                        else None
                    ),
                }
            )

            # Handle risk assessment parameters with null checks
            if hasattr(builder, "search_builder") and builder.search_builder:
                risk_mode = getattr(
                    builder.search_builder,
                    SearchCriteria.RiskAssessmentMode.value,
                    None,
                )
                if risk_mode is not None:
                    query_params["risk_assessment_mode"] = risk_mode

                risk_result = getattr(
                    builder.search_builder,
                    SearchCriteria.RiskAssessmentResult.value,
                    None,
                )
                if risk_result is not None:
                    query_params["risk_assessment_result"] = risk_result

                risk_reason = getattr(
                    builder.search_builder,
                    SearchCriteria.RiskAssessmentReasonCode.value,
                    None,
                )
                if risk_reason is not None:
                    query_params["risk_assessment_reason_code"] = risk_reason

                payment_provider = getattr(
                    builder.search_builder, SearchCriteria.PaymentProvider.value, None
                )
                if payment_provider is not None:
                    query_params["provider"] = str(payment_provider)

            query_params.update(self.get_transaction_params(builder))

        elif builder.report_type == ReportType.FindSettlementTransactionsPaged:
            endpoint = GpApiRequest.SETTLEMENT_TRANSACTIONS_ENDPOINT
            verb = HttpVerb.GET

            query_params["account_name"] = config.access_token_info.data_account_name
            query_params["account_id"] = config.access_token_info.data_account_id
            query_params["deposit_status"] = (
                getattr(
                    builder.search_builder, SearchCriteria.DepositStatus.value, None
                )
                if hasattr(builder, "search_builder")
                else None
            )
            query_params["arn"] = (
                getattr(
                    builder.search_builder,
                    SearchCriteria.AquirerReferenceNumber.value,
                    None,
                )
                if hasattr(builder, "search_builder")
                else None
            )

            if hasattr(builder, "search_builder"):
                deposit_id = getattr(
                    builder.search_builder, SearchCriteria.DepositId.value, None
                )
                if deposit_id:
                    query_params["deposit_id"] = deposit_id
                else:
                    deposit_reference = getattr(
                        builder.search_builder, "depositReference", None
                    )
                    if deposit_reference:
                        query_params["deposit_id"] = deposit_reference

                start_deposit_date = getattr(
                    builder.search_builder, "startDepositDate", None
                )
                if start_deposit_date:
                    if (
                        isinstance(start_deposit_date, str)
                        and "T" in start_deposit_date
                    ):
                        query_params["from_deposit_time_created"] = (
                            start_deposit_date.split("T")[0]
                        )
                    else:
                        # Handle datetime objects and other types safely
                        from datetime import datetime

                        if isinstance(start_deposit_date, datetime):
                            query_params["from_deposit_time_created"] = (
                                start_deposit_date.strftime("%Y-%m-%d")
                            )
                        else:
                            query_params["from_deposit_time_created"] = str(
                                start_deposit_date
                            )

                end_deposit_date = getattr(
                    builder.search_builder, "endDepositDate", None
                )
                if end_deposit_date:
                    if isinstance(end_deposit_date, str) and "T" in end_deposit_date:
                        query_params["to_deposit_time_created"] = (
                            end_deposit_date.split("T")[0]
                        )
                    else:
                        # Handle datetime objects and other types safely
                        from datetime import datetime

                        if isinstance(end_deposit_date, datetime):
                            query_params["to_deposit_time_created"] = (
                                end_deposit_date.strftime("%Y-%m-%d")
                            )
                        else:
                            query_params["to_deposit_time_created"] = str(
                                end_deposit_date
                            )

                start_batch_date = getattr(
                    builder.search_builder, "startBatchDate", None
                )
                if start_batch_date:
                    if isinstance(start_batch_date, str) and "T" in start_batch_date:
                        query_params["from_batch_time_created"] = (
                            start_batch_date.split("T")[0]
                        )
                    else:
                        # Handle datetime objects and other types safely
                        from datetime import datetime

                        if isinstance(start_batch_date, datetime):
                            query_params["from_batch_time_created"] = (
                                start_batch_date.strftime("%Y-%m-%d")
                            )
                        else:
                            query_params["from_batch_time_created"] = str(
                                start_batch_date
                            )

                end_batch_date = getattr(builder.search_builder, "endBatchDate", None)
                if end_batch_date:
                    if isinstance(end_batch_date, str) and "T" in end_batch_date:
                        query_params["to_batch_time_created"] = end_batch_date.split(
                            "T"
                        )[0]
                    else:
                        # Handle datetime objects and other types safely
                        from datetime import datetime

                        if isinstance(end_batch_date, datetime):
                            query_params["to_batch_time_created"] = (
                                end_batch_date.strftime("%Y-%m-%d")
                            )
                        else:
                            query_params["to_batch_time_created"] = str(end_batch_date)

                merchant_id = getattr(
                    builder.search_builder, SearchCriteria.MerchantId.value, None
                )
                if merchant_id:
                    query_params["system.mid"] = merchant_id

                system_hierarchy = getattr(
                    builder.search_builder, SearchCriteria.SystemHierarchy.value, None
                )
                if system_hierarchy:
                    query_params["system.hierarchy"] = system_hierarchy

            # Add transaction params
            query_params.update(self.get_transaction_params(builder))

        elif builder.report_type == ReportType.FindDepositsPaged:
            endpoint = GpApiRequest.DEPOSITS_ENDPOINT
            verb = HttpVerb.GET

            query_params["account_name"] = config.access_token_info.data_account_name
            query_params["account_id"] = config.access_token_info.data_account_id
            query_params["order_by"] = (
                builder.deposit_order_by
                if hasattr(builder, "deposit_order_by")
                else None
            )
            query_params["order"] = builder.order if hasattr(builder, "order") else None

            if hasattr(builder, "search_builder"):
                amount = getattr(
                    builder.search_builder, SearchCriteria.Amount.value, None
                )
                if amount is not None:
                    query_params["amount"] = StringUtils.to_numeric(amount)

                start_date = getattr(
                    builder.search_builder, SearchCriteria.StartDate.value, None
                )
                if start_date:
                    if isinstance(start_date, str) and "T" in start_date:
                        query_params["from_time_created"] = start_date.split("T")[0]
                    else:
                        # Handle datetime objects and other types safely
                        from datetime import datetime

                        if isinstance(start_date, datetime):
                            query_params["from_time_created"] = start_date.strftime(
                                "%Y-%m-%d"
                            )
                        else:
                            query_params["from_time_created"] = str(start_date)

                end_date = getattr(
                    builder.search_builder, SearchCriteria.EndDate.value, None
                )
                if end_date:
                    if isinstance(end_date, str) and "T" in end_date:
                        query_params["to_time_created"] = end_date.split("T")[0]
                    else:
                        # Handle datetime objects and other types safely
                        from datetime import datetime

                        if isinstance(end_date, datetime):
                            query_params["to_time_created"] = end_date.strftime(
                                "%Y-%m-%d"
                            )
                        else:
                            query_params["to_time_created"] = str(end_date)

                deposit_id = getattr(
                    builder.search_builder, SearchCriteria.DepositId.value, None
                )
                if deposit_id:
                    query_params["id"] = deposit_id

                deposit_status = getattr(
                    builder.search_builder, SearchCriteria.DepositStatus.value, None
                )
                if deposit_status:
                    query_params["status"] = deposit_status

                account_number_last_four = getattr(
                    builder.search_builder,
                    SearchCriteria.AccountNumberLastFour.value,
                    None,
                )
                if account_number_last_four:
                    query_params["masked_account_number_last4"] = (
                        account_number_last_four
                    )

                merchant_id = getattr(
                    builder.search_builder, SearchCriteria.MerchantId.value, None
                )
                if merchant_id:
                    query_params["system.mid"] = merchant_id

                system_hierarchy = getattr(
                    builder.search_builder, SearchCriteria.SystemHierarchy.value, None
                )
                if system_hierarchy:
                    query_params["system.hierarchy"] = system_hierarchy

        elif builder.report_type == ReportType.DepositDetail:
            deposit_id = getattr(
                builder.search_builder, SearchCriteria.DepositId.value, None
            )
            endpoint = f"{GpApiRequest.DEPOSITS_ENDPOINT}/{deposit_id}"
            verb = HttpVerb.GET

        elif builder.report_type == ReportType.DisputeDetail:
            dispute_id = getattr(
                builder.search_builder, SearchCriteria.DisputeId.value, None
            )
            endpoint = f"{GpApiRequest.DISPUTES_ENDPOINT}/{dispute_id}"
            verb = HttpVerb.GET

        elif builder.report_type == ReportType.DocumentDisputeDetail:
            dispute_id = getattr(
                builder.search_builder, SearchCriteria.DisputeId.value, None
            )
            dispute_doc_id = getattr(
                builder.search_builder, SearchCriteria.DisputeDocumentId.value, None
            )
            endpoint = f"{GpApiRequest.DISPUTES_ENDPOINT}/{dispute_id}/documents/{dispute_doc_id}"
            verb = HttpVerb.GET

        elif builder.report_type == ReportType.SettlementDisputeDetail:
            settlement_dispute_id = getattr(
                builder.search_builder, SearchCriteria.SettlementDisputeId.value, None
            )
            endpoint = (
                f"{GpApiRequest.SETTLEMENT_DISPUTES_ENDPOINT}/{settlement_dispute_id}"
            )
            verb = HttpVerb.GET

        elif builder.report_type == ReportType.FindSettlementDisputesPaged:
            endpoint = GpApiRequest.SETTLEMENT_DISPUTES_ENDPOINT
            verb = HttpVerb.GET

            # Get disputes params
            dispute_params = self.get_disputes_params(builder)
            query_params.update(dispute_params)

            query_params["account_name"] = config.access_token_info.data_account_name
            query_params["account_id"] = config.access_token_info.data_account_id

        elif builder.report_type == ReportType.FindDisputesPaged:
            endpoint = GpApiRequest.DISPUTES_ENDPOINT
            verb = HttpVerb.GET

            # Get disputes params
            dispute_params = self.get_disputes_params(builder)
            query_params.update(dispute_params)

        else:
            raise NotImplementedError("Report type not implemented")

        # Filter out None values from query parameters
        output = {}
        for k, v in query_params.items():
            if v is None:
                continue
            if isinstance(v, dt):
                output[k] = v.isoformat().split("T")[0]
            elif isinstance(v, Enum):
                output[k] = v.value
            else:
                output[k] = v

        return GpApiRequest(
            endpoint, verb, object_serialize(payload) if payload else "", output
        )

    @staticmethod
    def get_transaction_params(builder: Any) -> dict:
        """
        Get transaction parameters
        """
        params = {}

        if hasattr(builder, "transaction_order_by") and builder.transaction_order_by:
            params["order_by"] = StringUtils.convert_enum_value(
                builder.transaction_order_by
            )

        if hasattr(builder, "order") and builder.order:
            params["order"] = StringUtils.convert_enum_value(builder.order)

        if hasattr(builder, "search_builder"):

            card_number_first_six = getattr(
                builder.search_builder, SearchCriteria.CardNumberFirstSix.value, None
            )
            if card_number_first_six:
                params["number_first6"] = card_number_first_six

            card_number_last_four = getattr(
                builder.search_builder, SearchCriteria.CardNumberLastFour.value, None
            )
            if card_number_last_four:
                params["number_last4"] = card_number_last_four

            card_brand = getattr(
                builder.search_builder, SearchCriteria.CardBrand.value, None
            )
            if card_brand:
                params["brand"] = card_brand

            brand_reference = getattr(
                builder.search_builder, SearchCriteria.BrandReference.value, None
            )
            if brand_reference:
                params["brand_reference"] = brand_reference

            auth_code = getattr(
                builder.search_builder, SearchCriteria.AuthCode.value, None
            )
            if auth_code:
                params["authcode"] = auth_code

            reference_number = getattr(
                builder.search_builder, SearchCriteria.ReferenceNumber.value, None
            )
            if reference_number:
                params["reference"] = reference_number

            start_date = getattr(
                builder.search_builder, SearchCriteria.StartDate.value, None
            )
            if start_date:
                params["from_time_created"] = start_date

            end_date = getattr(
                builder.search_builder, SearchCriteria.EndDate.value, None
            )
            if end_date:
                params["to_time_created"] = end_date

            transaction_status = getattr(
                builder.search_builder, SearchCriteria.TransactionStatus.value, None
            )
            if transaction_status:
                params["status"] = transaction_status

        return params

    def get_disputes_params(self, builder: Any) -> dict:
        """
        Get disputes parameters
        """
        params = {}

        if hasattr(builder, "search_builder"):
            dispute_status = getattr(
                builder.search_builder, SearchCriteria.DisputeStatus.value, None
            )
            if dispute_status:
                params["status"] = dispute_status

            start_date = getattr(
                builder.search_builder, SearchCriteria.StartDate.value, None
            )
            if start_date:
                params["from"] = start_date

            end_date = getattr(
                builder.search_builder, SearchCriteria.EndDate.value, None
            )
            if end_date:
                params["to"] = end_date

            dispute_stage = getattr(
                builder.search_builder, SearchCriteria.DisputeStage.value, None
            )
            if dispute_stage:
                params["stage"] = dispute_stage

            # For dispute reason - not in SearchCriteria enum
            dispute_reason = getattr(builder.search_builder, "disputeReason", None)
            if dispute_reason:
                params["reason"] = dispute_reason

        return params

    def build_request_from_json(self, json_request: str, config: Any = None) -> Any:
        """
        Builds a request from a JSON string

        Args:
            json_request: The JSON string to build from
            config: The configuration to use

        Returns:
            The built request
        """
        # TODO: Implement this method
        pass
