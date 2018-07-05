"""
Setup for GlobalPayments.Api
"""

from distutils.core import setup

setup(
    name='GlobalPayments.Api',
    version='1.0.1',
    author='Heartland Payment Systems',
    author_email='EntApp_DevPortal@e-hps.com',
    packages=[
        'globalpayments', 'globalpayments.api', 'globalpayments.api.builders',
        'globalpayments.api.builders.validations',
        'globalpayments.api.entities',
        'globalpayments.api.entities.table_service',
        'globalpayments.api.gateways', 'globalpayments.api.payment_methods',
        'globalpayments.api.services', 'globalpayments.api.utils'
    ],
    scripts=[],
    url='https://developer.heartlandpaymentsystems.com/',
    license='LICENSE.md',
    description='',
    long_description=open('README.txt').read(),
    install_requires=[
        'xmltodict >= 0.9.0', 'jsonpickle >= 0.6.1', 'enum34 >= 1.1.6',
        'urllib3[secure] >= 1.18', 'certifi >= 2016.9.26',
        'pyopenssl >= 17.5.0'
    ])
