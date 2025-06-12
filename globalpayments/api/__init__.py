"""
globalpayments.api module
"""

import dataclasses
from typing import Dict, List, Optional, Any, Union

# Import the key submodules to make them available as attributes
import globalpayments.api.builders as builders
import globalpayments.api.entities as entities
import globalpayments.api.gateways as gateways
import globalpayments.api.payment_methods as payment_methods
import globalpayments.api.services as services
import globalpayments.api.utils as utils

# Direct imports for entities and enums
from globalpayments.api.entities.enums import (
    FraudFilterMode,
    HppVersion,
    ReservationProviders,
    GatewayProvider,
    CardChannel,
    Environment,
    ThreeDSecureVersion,
)
from globalpayments.api.entities.exceptions import ConfigurationException
from globalpayments.api.entities.gp_api import AccessTokenInfo
from globalpayments.api.gateways import (
    PayPlanConnector,
    PorticoConnector,
    RealexConnector,
    TableServiceConnector,
)


class HostedPaymentConfig(object):
    """
    Hosted Payment Page (HPP) configuration
    This configuration is used when constructing HPP requests to be used by
    a client library (JS, iOS, Android).
    """

    #  Allow card to be stored within the HPP
    card_storage_enabled: Optional[bool] = None
    #  Allow Dynamic Currency Conversion (DCC) to be available
    dynamic_currency_conversion_enabled: Optional[bool] = None
    #  Allow a consumer's previously stored cards to be shown
    display_saved_cards: Optional[bool] = None
    #  Manner in which the fraud filter should operate
    fraud_filter_mode: FraudFilterMode = FraudFilterMode.NONE
    #  The desired language for the HPP
    language: Optional[str] = None
    #  Text for the HPP's submit button
    payment_button_text: Optional[str] = None
    #  URL to receive `POST` data of the HPP's result
    response_url: Optional[str] = None
    #  Denotes if Transaction Stability Score (TSS) should be active
    request_transaction_stability_score: Optional[bool] = None
    #  Specify HPP version
    version: HppVersion = HppVersion.VERSION_1
    #  iFrame Optimisation - dimensions
    post_dimensions: Optional[str] = None
    #  iFrame Optimisation - response
    post_response: Optional[str] = None


@dataclasses.dataclass
class GatewayConfig(object):
    """
    Configuration for connecting to a payment gateway
    """

    gateway_provider: Optional[GatewayProvider] = None
    #  Gateway Service URL
    service_url: Optional[str] = None
    #  Timeout value for gateway communication (in milliseconds)
    timeout: Optional[int] = 65000

    def validate(self) -> None:
        pass


class ConfiguredServices(object):
    gateway_connector: Optional[Any] = None
    recurring_connector: Optional[Any] = None
    device_interface: Optional[Any] = None
    device_controller: Optional[Any] = None
    reservation_connector: Optional[Any] = None
    reporting_service: Optional[Any] = None
    secure_3d_provider: Optional[Dict[ThreeDSecureVersion, Any]] = None


SERVICE_CONTAINER_INSTANCE = None


@dataclasses.dataclass
class GpApiConfig(GatewayConfig):
    gateway_provider: GatewayProvider = GatewayProvider.GpApi
    seconds_to_expire: Optional[int] = None
    interval_to_expire: Optional[int] = None
    permissions: Optional[List[str]] = None
    app_id: Optional[str] = None
    app_key: Optional[str] = None
    channel: Optional[CardChannel] = None
    environment: Optional[Environment] = None
    access_token_info: Optional[AccessTokenInfo] = None
    merchant_id: Optional[str] = None
    country: Optional[str] = None
    challenge_notification_url: Optional[str] = None
    method_notification_url: Optional[str] = None
    merchant_contact_url: Optional[str] = None
    dynamic_headers: Optional[Dict[str, str]] = None
    request_logger: Optional[Any] = None


@dataclasses.dataclass
class PorticoConfig(GatewayConfig):
    gateway_provider: GatewayProvider = GatewayProvider.Portico
    #  Account's site ID
    site_id: Optional[Union[str, int]] = None
    #  Account's license ID
    license_id: Optional[Union[str, int]] = None
    #  Account's device ID
    device_id: Optional[Union[str, int]] = None
    #  Account's username
    username: Optional[str] = None
    #  Account's password
    password: Optional[str] = None
    """
    Integration's developer ID
    This is provided at the start of an integration's certification
    """
    developer_id: Optional[str] = None
    """
    Integration's version number
    This is provided at the start of an integration's certification
    """
    version_number: Optional[str] = None
    #  Account's secret API Key
    secret_api_key: Optional[str] = None
    #  Account's account ID
    account_id: Optional[str] = None
    # Account's merchant ID
    merchant_id: Optional[str] = None
    #  Account's rebate password
    rebate_password: Optional[str] = None
    #  Account's refund password
    refund_password: Optional[str] = None
    #  Account's shared secret
    shared_secret: Optional[str] = None
    #  Channel for an integration's transactions (e.g. "internet")
    channel: Optional[str] = None
    #  Hosted Payment Page (HPP) configuration
    hosted_payment_config: Optional[HostedPaymentConfig] = None
    #  Connection details for physical card reader device
    device_connection_config: Optional[Any] = None
    #  Connection details for the reservation service
    reservation_provider: Optional[ReservationProviders] = None

    def validate(self) -> None:
        #  portico api key
        if self.secret_api_key is not None:
            if (
                self.site_id is not None
                or self.license_id is not None
                or self.device_id is not None
                or self.username is not None
                or self.password is not None
            ):
                raise ConfigurationException(
                    """Configuration contains both secret api key and legacy credentials.
                    These are mutually exclusive."""
                )

        #  legacy portico
        if (
            self.site_id is not None
            or self.license_id is not None
            or self.device_id is not None
            or self.username is not None
            or self.password is not None
        ):
            if (
                self.site_id is None
                or self.license_id is None
                or self.device_id is None
                or self.username is None
                or self.password is None
            ):
                raise ConfigurationException(
                    """Site, License, Device, Username and Password should all have a
                    values for this configuration."""
                )

        #  realex
        if self.merchant_id is not None or self.shared_secret is not None:
            if self.merchant_id is None:
                raise ConfigurationException(
                    "merchant_id is required for this configuration."
                )
            if self.shared_secret is None:
                raise ConfigurationException(
                    "shared_secret is required for this configuration."
                )

        #  service url
        if self.service_url is None:
            pass


class ServicesContainer(object):
    """
    Maintains references to the currently configured gateway/device objects
    The 'ServicesContainer.configure' method is the only call
    required of the integrator to configure the SDK's various gateway/device
    interactions. The configured gateway/device objects are handled
    internally by exposed APIs throughout the SDK.
    """

    _configurations = None

    @staticmethod
    def instance():
        global SERVICE_CONTAINER_INSTANCE

        if SERVICE_CONTAINER_INSTANCE is not None:
            return SERVICE_CONTAINER_INSTANCE
        raise ConfigurationException("Services container not configured.")

    @staticmethod
    def remove_configuration(config_name="default"):
        global SERVICE_CONTAINER_INSTANCE
        if SERVICE_CONTAINER_INSTANCE is None:
            SERVICE_CONTAINER_INSTANCE = ServicesContainer()

        SERVICE_CONTAINER_INSTANCE.remove_config(config_name)

    @staticmethod
    def configure(config, config_name="default"):
        global SERVICE_CONTAINER_INSTANCE

        if not isinstance(config, GatewayConfig):
            raise ConfigurationException("config must be of type ServiceConfig")
        config.validate()

        cs = ConfiguredServices()

        #  configure devices
        # if config.device_connection_config is not None:
        #     if config.device_connection_config.device_type is DeviceType.PAX_S300:
        #         device_controller = PaxController(config.device_connection_config)
        #     elif config.device_connection_config.device_type is DeviceType.HSIP_ISC250:
        #         device_controller = HeartSipController(config.device_connection_config)
        #
        #     if device_controller is not None:
        #         device_interface = device_controller.configure_interface()

        if isinstance(config, GpApiConfig):
            gateway = gateways.GpApiConnector(config)
            gateway.service_url = config.service_url or "https://apis.globalpay.com/ucp"
            config.gateway_provider = GatewayProvider.GpApi

            # Set various services
            cs.gateway_connector = gateway
            cs.reporting_service = gateway
            cs.secure_3d_provider = {
                ThreeDSecureVersion.One: gateway,
                ThreeDSecureVersion.Two: gateway,
            }

        if isinstance(config, PorticoConfig):
            # configure reservations
            config.gateway_provider = GatewayProvider.Portico
            if config.reservation_provider is not None:
                if config.reservation_provider is ReservationProviders.FreshTxt:
                    cs.reservation_connector = TableServiceConnector()
                    cs.reservation_connector.service_url = (
                        "https://www.freshtxt.com/api31/"
                    )
                    cs.reservation_connector.timeout = config.timeout

            # configure gateways
            if config.merchant_id is not None:
                cs.gateway_connector = RealexConnector()
                cs.gateway_connector.account_id = config.account_id
                cs.gateway_connector.channel = config.channel
                cs.gateway_connector.merchant_id = config.merchant_id
                cs.gateway_connector.rebate_password = config.rebate_password
                cs.gateway_connector.refund_password = config.refund_password
                cs.gateway_connector.shared_secret = config.shared_secret
                cs.gateway_connector.timeout = config.timeout
                cs.gateway_connector.service_url = config.service_url
                cs.gateway_connector.hosted_payment_config = (
                    config.hosted_payment_config
                )
                cs.recurring_connector = cs.gateway_connector
            else:
                cs.gateway_connector = PorticoConnector()
                cs.gateway_connector.site_id = config.site_id
                cs.gateway_connector.license_id = config.license_id
                cs.gateway_connector.device_id = config.device_id
                cs.gateway_connector.username = config.username
                cs.gateway_connector.password = config.password
                cs.gateway_connector.secret_api_key = config.secret_api_key
                cs.gateway_connector.developer_id = config.developer_id
                cs.gateway_connector.version_number = config.version_number
                cs.gateway_connector.timeout = config.timeout
                cs.gateway_connector.service_url = (
                    config.service_url or ""
                ) + "/Hps.Exchange.PosGateway/PosGatewayService.asmx"

                cs.recurring_connector = PayPlanConnector()
                cs.recurring_connector.secret_api_key = config.secret_api_key
                cs.recurring_connector.timeout = config.timeout
                cs.recurring_connector.service_url = (
                    config.service_url or ""
                ) + "/Portico.PayPlan.v2/"

        if SERVICE_CONTAINER_INSTANCE is None:
            SERVICE_CONTAINER_INSTANCE = ServicesContainer()

        SERVICE_CONTAINER_INSTANCE.add_configuration(config_name, cs)

    def __init__(self):
        self._configurations = {}

    def add_configuration(self, config_name, config):
        if self._configurations is not None:
            self._configurations[config_name] = config

    def get_client(self, config_name):
        if self._configurations is not None and config_name in self._configurations:
            return self._configurations[config_name].gateway_connector
        return None

    def remove_config(self, config_name):
        if self._configurations is not None and config_name in self._configurations:
            del self._configurations[config_name]

    def get_device_interface(self, config_name):
        if self._configurations is not None and config_name in self._configurations:
            return self._configurations[config_name].device_interface
        return None

    def get_device_controller(self, config_name):
        if self._configurations is not None and config_name in self._configurations:
            return self._configurations[config_name].device_controller
        return None

    def get_recurring_client(self, config_name):
        if self._configurations is not None and config_name in self._configurations:
            return self._configurations[config_name].recurring_connector
        return None

    def get_reservation_service(self, config_name):
        if self._configurations is not None and config_name in self._configurations:
            return self._configurations[config_name].reservation_connector
        return None

    def get_secure_3d(self, config_name, version: Optional[ThreeDSecureVersion] = None):
        if self._configurations is not None and config_name in self._configurations:
            if version is None:
                return None
            return self._configurations[config_name].secure_3d_provider.get(version)
        return None
