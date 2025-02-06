"""
Test gift
"""

import unittest
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.payment_methods import GiftCard


class IntegrationGatewaysPorticoConnectorEbtTests(unittest.TestCase):
    """
    Ensure gift transactions work
    """

    config = PorticoConfig()
    config.secret_api_key = "skapi_cert_MaePAQBr-1QAqjfckFC8FTbRTT120bVQUlfVOjgCBw"
    config.service_url = "https://cert.api2.heartlandportico.com"
    config.developer_id = "000000"
    config.version_number = "0000"

    ServicesContainer.configure(config, "gift")

    card = GiftCard()
    card.number = "5022440000000000007"

    track = GiftCard()
    track.track_data = (
        "%B5022440000000000098^^391200081613?;5022440000000000098=391200081613?"
    )

    def test_gift_create(self):
        new_card = GiftCard.create("2145550199", config_name="gift")

        self.assertNotEqual(None, new_card)
        self.assertNotEqual(None, new_card.number)
        self.assertNotEqual(None, new_card.alias)
        self.assertNotEqual(None, new_card.pin)

    def test_gift_add_alias(self):
        response = self.card.add_alias("2145550199").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_add_value(self):
        response = self.card.add_value(10).with_currency("USD").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_balance_inquiry(self):
        response = self.card.balance_inquiry().execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_sale(self):
        response = self.card.charge(10).with_currency("USD").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_deactivate(self):
        response = self.card.deactivate().execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_remove_alias(self):
        response = self.card.remove_alias("2195550199").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_replace(self):
        response = self.card.replace_with(self.track).execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_reverse(self):
        response = self.card.reverse(10).execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_reward(self):
        response = self.card.rewards(10).execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_add_alias(self):
        response = self.track.add_alias("2145550199").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_add_value(self):
        response = self.track.add_value(10).with_currency("USD").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_balance_inquiry(self):
        response = self.track.balance_inquiry().execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_sale(self):
        response = self.track.charge(10).with_currency("USD").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_deactivate(self):
        response = self.track.deactivate().execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_remove_alias(self):
        response = self.track.remove_alias("2195550199").execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_replace(self):
        response = self.track.replace_with(self.card).execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_reverse(self):
        response = self.track.reverse(10).execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)

    def test_gift_track_reward(self):
        response = self.track.rewards(10).execute("gift")

        self.assertNotEqual(None, response)
        self.assertEqual("00", response.response_code)
