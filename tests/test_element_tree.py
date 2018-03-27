import unittest
from globalpayments.api.utils import ElementTree
from globalpayments.api.builders import *


class ElementTreeTests(unittest.TestCase):
    def test_tree_creation(self):
        et = ElementTree()
        builder = AuthorizationBuilder(TransactionType.Auth)
        self.assertIsNotNone(et)
