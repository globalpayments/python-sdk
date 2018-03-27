"""
Test runner for GlobalPayments.Api
"""

from unittest import TextTestRunner, TestLoader

if __name__ == "__main__":
    TextTestRunner().run(TestLoader().discover('.'))
