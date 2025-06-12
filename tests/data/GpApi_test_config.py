""" Test Credit with GpApi """

from globalpayments.api import GpApiConfig
from globalpayments.api import ServicesContainer

from globalpayments.api.entities.enums import CardChannel, Environment
from globalpayments.api.entities.gp_api import AccessTokenInfo
from globalpayments.api.utils.logger import Logger


class GpApiTestConfig:
    """
    Configuration for GpApi tests
    """

    PARTNER_SOLUTION_APP_ID = "A1feRdMmEB6m0Y1aQ65H0bDi9ZeAEB2t"
    PARTNER_SOLUTION_APP_KEY = "5jPt1OpB6LLitgi7"

    app_id = "4gPqnGBkppGYvoE5UX9EWQlotTxGUDbs"
    app_key = "FQyJA5VuEQfcji2M"

    UPA_MIC_DEVICE_APP_ID = "83cdNQ0YBmzxzkLpFHpDGn2ir0WKTW0N"
    UPA_MIC_DEVICE_APP_KEY = "1ASrcQZb0AEqR6ZT"

    _dynamic_header_enabled = False
    _permissions_enabled = False
    _log_enabled = True

    @staticmethod
    def gpapi_setup_config(channel: CardChannel):
        config = GpApiConfig()
        config.app_id = GpApiTestConfig.app_id
        config.app_key = GpApiTestConfig.app_key
        config.service_url = "https://apis.sandbox.globalpay.com/ucp"
        config.environment = Environment.Test
        config.channel = channel
        config.country = "US"
        config.access_token_info = AccessTokenInfo()
        config.access_token_info.transaction_processing_account_name = (
            "transaction_processing"
        )
        config.access_token_info.transaction_processing_account_id = (
            "TRA_c9967ad7d8ec4b46b6dd44a61cde9a91"
        )
        config.access_token_info.risk_assessment_account_name = "EOS_RiskAssessment"

        config.challenge_notification_url = "https://ensi808o85za.x.pipedream.net/"
        config.method_notification_url = "https://ensi808o85za.x.pipedream.net/"
        config.merchant_contact_url = "https://ensi808o85za.x.pipedream.net/"

        if GpApiTestConfig._dynamic_header_enabled:
            config.dynamic_headers = {
                "x-gp-platform": "prestashop;version=1.7.2",
                "x-gp-extension": "coccinet;version=2.4.1",
            }

        if GpApiTestConfig._permissions_enabled:
            config.permissions = ["TRN_POST_Authorize"]

        if GpApiTestConfig._log_enabled:
            config.request_logger = Logger()

        return config

    @staticmethod
    def reset_gpapi_config():
        ServicesContainer.remove_configuration()
        GpApiTestConfig.app_id = GpApiTestConfig.app_id
        GpApiTestConfig.app_key = GpApiTestConfig.app_key
