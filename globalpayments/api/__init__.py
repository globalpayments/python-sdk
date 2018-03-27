"""
"""

from globalpayments.api.entities.enums import (
    FraudFilterMode,
    HppVersion,
    ReservationProviders,
)
from globalpayments.api.entities.exceptions import ConfigurationException
from globalpayments.api.gateways import (
    PayPlanConnector, PorticoConnector, RealexConnector, TableServiceConnector)


class HostedPaymentConfig(object):
    """
    Hosted Payment Page (HPP) configuration
    This configuration is used when constructing HPP requests to be used by
    a client library (JS, iOS, Android).
    """

    #  Allow card to be stored within the HPP
    card_storage_enabled = None
    #  Allow Dynamic Currency Conversion (DCC) to be available
    dynamic_currency_conversion_enabled = None
    #  Allow a consumer's previously stored cards to be shown
    display_saved_cards = None
    #  Manner in which the fraud filter should operate
    fraud_filter_mode = FraudFilterMode.NONE
    #  The desired language for the HPP
    language = None
    #  Text for the HPP's submit button
    payment_button_text = None
    #  URL to receive `POST` data of the HPP's result
    response_url = None
    #  Denotes if Transaction Stability Score (TSS) should be active
    request_transaction_stability_score = None
    #  Specify HPP version
    version = HppVersion.VERSION_1
    #  iFrame Optimisation - dimensions
    post_dimensions = None
    #  iFrame Optimisation - response
    post_response = None


class ServicesConfig(object):
    """
    Configuration for connecting to a payment gateway
    """

    #  Account's site ID
    site_id = None
    #  Account's license ID
    license_id = None
    #  Account's device ID
    device_id = None
    #  Account's username
    username = None
    #  Account's password
    password = None
    """
    Integration's developer ID
    This is provided at the start of an integration's certification
    """
    developer_id = None
    """
    Integration's version number
    This is provided at the start of an integration's certification
    """
    version_number = None
    #  Account's secret API Key
    secret_api_key = None
    #  Account's account ID
    account_id = None
    # Account's merchant ID
    merchant_id = None
    #  Account's rebate password
    rebate_password = None
    #  Account's refund password
    refund_password = None
    #  Account's shared secret
    shared_secret = None
    #  Channel for an integration's transactions (e.g. "internet")
    channel = None
    #  Hosted Payment Page (HPP) configuration
    hosted_payment_config = None
    #  Connection details for physical card reader device
    device_connection_config = None
    #  Connection details for the reservation service
    reservation_provider = None
    #  Gateway Service URL
    service_url = None
    #  Timeout value for gateway communication (in milliseconds)
    timeout = None

    def __init__(self):
        self.timeout = 65000

    def validate(self):
        #  portico api key
        if self.secret_api_key is not None:
            if (self.site_id is not None or self.license_id is not None
                    or self.device_id is not None or self.username is not None
                    or self.password is not None):
                raise ConfigurationException(
                    """Configuration contains both secret api key and legacy credentials.
                    These are mutually exclusive.""")

        #  legacy portico
        if (self.site_id is not None or self.license_id is not None
                or self.device_id is not None or self.username is not None
                or self.password is not None):
            if (self.site_id is None or self.license_id is None
                    or self.device_id is None or self.username is None
                    or self.password is None):
                raise ConfigurationException(
                    """Site, License, Device, Username and Password should all have a
                    values for this configuration.""")

        #  realex
        if self.merchant_id is not None or self.shared_secret is not None:
            if self.merchant_id is None:
                raise ConfigurationException(
                    'merchant_id is required for this configuration.')
            if self.shared_secret is None:
                raise ConfigurationException(
                    'shared_secret is required for this configuration.')

        #  service url
        if self.service_url is None:
            pass


class ConfiguredServices(object):
    gateway_connector = None
    recurring_connector = None
    device_interface = None
    device_controller = None
    reservation_connector = None


SERVICE_CONTAINER_INSTANCE = None


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
        raise ConfigurationException('Services container not configured.')

    @staticmethod
    def configure(config, config_name="default"):
        global SERVICE_CONTAINER_INSTANCE

        if not isinstance(config, ServicesConfig):
            raise ConfigurationException(
                'config must be of type ServiceConfig')

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

        # configure reservations
        if config.reservation_provider is not None:
            if config.reservation_provider is ReservationProviders.FreshTxt:
                cs.reservation_connector = TableServiceConnector()
                cs.reservation_connector.service_url = 'https://www.freshtxt.com/api31/'
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
            cs.gateway_connector.hosted_payment_config = config.hosted_payment_config
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
            cs.gateway_connector.service_url = config.service_url \
                + '/Hps.Exchange.PosGateway/PosGatewayService.asmx'

            cs.recurring_connector = PayPlanConnector()
            cs.recurring_connector.secret_api_key = config.secret_api_key
            cs.recurring_connector.timeout = config.timeout
            cs.recurring_connector.service_url = config.service_url + '/Portico.PayPlan.v2/'

        if SERVICE_CONTAINER_INSTANCE is None:
            SERVICE_CONTAINER_INSTANCE = ServicesContainer()

        SERVICE_CONTAINER_INSTANCE.add_configuration(config_name, cs)

    def __init__(self):
        self._configurations = {}

    def add_configuration(self, config_name, config):
        self._configurations[config_name] = config

    def get_client(self, config_name):
        if config_name in self._configurations:
            return self._configurations[config_name].gateway_connector
        return None

    def get_device_interface(self, config_name):
        if config_name in self._configurations:
            return self._configurations[config_name].device_interface
        return None

    def get_device_controller(self, config_name):
        if config_name in self._configurations:
            return self._configurations[config_name].device_controller
        return None

    def get_recurring_client(self, config_name):
        if config_name in self._configurations:
            return self._configurations[config_name].recurring_connector
        return None

    def get_reservation_service(self, config_name):
        if config_name in self._configurations:
            return self._configurations[config_name].reservation_connector
        return None
