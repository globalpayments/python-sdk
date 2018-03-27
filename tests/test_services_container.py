"""
Test GlobalPayments.Api.ServicesContainer
"""

import unittest
from globalpayments.api import ServicesConfig, ServicesContainer
from globalpayments.api.gateways import PorticoConnector


class TestServicesContainer(unittest.TestCase):
    """
    Test GlobalPayments.Api.ServicesContainer
    """

    config = ServicesConfig()
    config.secret_api_key = 'skapi_cert_MTeSAQAfG1UA9qQDrzl-kz4toXvARyieptFwSKP24w'
    config.service_url = 'https://cert.api2.heartlandportico.com'

    ServicesContainer.configure(config)

    def test_container_instance(self):
        """
        Ensures configured gateway instance is available
        """
        gateway = ServicesContainer.instance().get_client("default")
        self.assertIsNotNone(gateway)
        self.assertTrue(isinstance(gateway, PorticoConnector))
