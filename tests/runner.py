"""
Test runner for GlobalPayments.Api
"""

from unittest import TextTestRunner, TestLoader, TestSuite

from tests.integration.gateways.GpApi_connector import (
    gpapi_test_reporting_transactions,
    gpapi_test_credit_card_not_present,
    gpapi_test_debit,
    gpapi_test_3DSecure,
)
from tests.integration.gateways.portico_connector import (
    test_credit,
    test_debit,
    test_ebt,
    test_ecommerce,
    test_gift,
    test_recurring,
    test_reporting,
    test_token_management,
)


def run_tests():
    TextTestRunner().run(TestLoader().discover(""))


def portico_tests():
    suite = TestSuite()
    # Add test modules to the suite
    suite.addTests(TestLoader().loadTestsFromModule(test_credit))
    suite.addTests(TestLoader().loadTestsFromModule(test_debit))
    suite.addTests(TestLoader().loadTestsFromModule(test_ebt))
    suite.addTests(TestLoader().loadTestsFromModule(test_ecommerce))
    suite.addTests(TestLoader().loadTestsFromModule(test_gift))
    suite.addTests(TestLoader().loadTestsFromModule(test_recurring))
    suite.addTests(TestLoader().loadTestsFromModule(test_reporting))
    suite.addTests(TestLoader().loadTestsFromModule(test_token_management))

    # Run all tests in the suite
    TextTestRunner().run(suite)


def gpapi_tests():
    suite = TestSuite()
    # Add test modules to the suite
    suite.addTests(TestLoader().loadTestsFromModule(gpapi_test_credit_card_not_present))
    suite.addTests(TestLoader().loadTestsFromModule(gpapi_test_debit))
    suite.addTests(TestLoader().loadTestsFromModule(gpapi_test_reporting_transactions))
    suite.addTests(TestLoader().loadTestsFromModule(gpapi_test_3DSecure))

    # Run all tests in the suite
    TextTestRunner().run(suite)


if __name__ == "__main__":
    run_tests()
