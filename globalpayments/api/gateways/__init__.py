'''
'''

import base64
import xml.etree.cElementTree as et
import re
import certifi
import jsonpickle
import urllib3.contrib.pyopenssl
import xmltodict
import globalpayments as gp
from globalpayments.api.entities import (
    Address, BatchSummary, Customer, DebitMac, RecurringPaymentMethod,
    Schedule, ThreeDSecure, Transaction, TransactionSummary)
from globalpayments.api.entities.enums import (
    AccountType, AddressType, AliasAction, CheckType, EmvChipCondition,
    EntryMethod, FraudFilterMode, HppVersion, PaymentMethodType,
    PaymentSchedule, ReportType, SecCode, TransactionType, TransactionModifier)
from globalpayments.api.entities.exceptions import (
    ApiException, BuilderException, GatewayException,
    UnsupportedTransactionException)
from globalpayments.api.gateways.gateway_response import GatewayResponse
from globalpayments.api.gateways.table_service_connector import TableServiceConnector
from globalpayments.api.payment_methods import (
    Balanceable, CardData, Credit, CreditCardData, ECheck, Encryptable,
    GiftCard, PaymentMethod, PinProtected, TrackData, Tokenizable,
    TransactionReference)
from globalpayments.api.utils import GenerationUtils

urllib3.contrib.pyopenssl.inject_into_urllib3()
HTTP = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


class Gateway(object):
    _content_type = None
    headers = {}
    timeout = None
    service_url = None

    def __init__(self, content_type):
        self._content_type = content_type

    def send_request(self, verb, endpoint, data=None,
                     query_string_params=None):
        query_string = self._build_query_string(query_string_params)
        url = self.service_url + endpoint + query_string
        request_headers = {'Content-Type': self._content_type}
        for key in self.headers:
            request_headers[key] = self.headers[key]

        try:
            request = HTTP.request(
                verb, url, headers=request_headers, body=data)
            raw_response = request.data
            response = GatewayResponse()
            response.status_code = request.status
            response.raw_response = raw_response
            return response
        except Exception as exc:
            raise GatewayException(
                'Error occurred while communicating with gateway.', exc)

    @staticmethod
    def _build_query_string(query_string_params):
        if query_string_params is None:
            return ''
        return ''


class RestGateway(Gateway):
    def __init__(self):
        Gateway.__init__(self, 'application/json')

    def do_transaction(self,
                       verb,
                       endpoint,
                       data=None,
                       query_string_params=None):
        response = self.send_request(verb, endpoint, data, query_string_params)
        if response.status_code is not 200 and response.status_code is not 204:
            parsed = jsonpickle.decode(response.raw_response)
            error = parsed if 'error' not in parsed else parsed['error']
            raise GatewayException('Status Code: {} - {}'.format(
                response.status_code, error['message']))
        return response.raw_response


class XmlGateway(Gateway):
    def __init__(self):
        Gateway.__init__(self, 'text/xml')

    def do_transaction(self, request):
        response = self.send_request('POST', '', request)
        if response.status_code is not 200:
            raise GatewayException('Unexpected http status code [{}]'.format(
                response.status_code))
        return response.raw_response


class PayPlanConnector(RestGateway):
    _secret_api_key = None

    @property
    def secret_api_key(self):
        return self._secret_api_key

    @secret_api_key.setter
    def secret_api_key(self, value):
        self._secret_api_key = value
        encoded_value = base64.b64encode(bytearray(value.encode()))
        self.headers['Authorization'] = 'Basic {}'.format(encoded_value)

    @property
    def supports_retrieval(self):
        return True

    @property
    def supports_update_payment_details(self):
        return False

    def __init__(self):
        RestGateway.__init__(self)

    def process_recurring(self, builder):
        request = {}

        if (builder.transaction_type is TransactionType.Create
                | builder.transaction_type is TransactionType.Edit):
            if isinstance(builder.entity, Customer):
                self._build_customer(request, builder.entity)
            elif isinstance(builder.entity, RecurringPaymentMethod):
                self._build_payment_method(request, builder.entity,
                                           builder.transaction_type)
            elif isinstance(builder.entity, Schedule):
                self._build_schedule(request, builder.entity,
                                     builder.transaction_type)
        elif builder.transaction_type is TransactionType.Search:
            for key, value in builder.search_criteria:
                request[key] = value

        response = self.do_transaction(
            self._map_method(builder.transaction_type), self._map_url(builder),
            jsonpickle.encode(request, False, False, False))
        return self._map_response(response, builder)

    def _map_response(self, raw_response, builder):
        if raw_response is None or raw_response == '':
            return None

        response = jsonpickle.decode(raw_response)

        if isinstance(builder.entity, Customer
                      ) and builder.transaction_type == TransactionType.Search:
            customers = []

            for _key, value in response.results:
                customers.append(self._hydrate_customer(value))

            return customers

        if isinstance(builder.entity, Customer):
            return self._hydrate_customer(response)

        if isinstance(builder.entity, RecurringPaymentMethod
                      ) and builder.transaction_type == TransactionType.Search:
            methods = []

            for _key, value in response.results:
                methods.append(self._hydrate_payment_method(value))

            return methods

        if isinstance(builder.entity, RecurringPaymentMethod):
            return self._hydrate_payment_method(response)

        if isinstance(builder.entity, Schedule
                      ) and builder.transaction_type == TransactionType.Search:
            schedules = []

            for _key, value in response.results:
                schedules.append(self._hydrate_schedule(value))

            return schedules

        if isinstance(builder.entity, Schedule):
            return self._hydrate_schedule(response)

        return response

    @staticmethod
    def _map_method(transaction_type):
        if transaction_type == TransactionType.Create | transaction_type == TransactionType.Search:
            return 'POST'
        elif transaction_type == TransactionType.Edit:
            return 'PUT'
        elif transaction_type == TransactionType.Delete:
            return 'DELETE'

        return 'GET'

    def _map_url(self, builder):
        suffix = ''
        if (builder.transaction_type == TransactionType.Fetch
                or builder.transaction_type == TransactionType.Delete
                or builder.transaction_type == TransactionType.Edit):
            suffix = '/' + builder.entity.key

        if isinstance(builder.entity, Customer):
            return '{}{}'.format(
                'searchCustomers' \
                    if builder.transaction_type == TransactionType.Search \
                    else 'customers',
                suffix
            )

        if isinstance(builder.entity, RecurringPaymentMethod):
            payment_method = ''

            if builder.transaction_type == TransactionType.Create:
                payment_method = 'CreditCard' \
                    if isinstance(builder.entity.payment_method, Credit) \
                    else 'ACH'
            elif builder.transaction_type == TransactionType.Edit:
                payment_method = builder.entity.payment_type.replace(' ', '')

            return '{}{}{}'.format(
                'searchPaymentMethods' \
                    if builder.transaction_type == TransactionType.Search \
                    else 'paymentMethods',
                payment_method,
                suffix
            )

        if isinstance(builder.entity, Schedule):
            return '{}{}'.format(
                'searchSchedules' \
                    if builder.transaction_type == TransactionType.Search \
                    else 'schedules',
                suffix
            )

        raise UnsupportedTransactionException()

    def _build_customer(self, request, customer):
        if customer is None:
            return request

        request['customerIdentifier'] = customer.id
        request['firstName'] = customer.first_name
        request['lastName'] = customer.last_name
        request['company'] = customer.company
        request['customerStatus'] = customer.status
        request['primaryEmail'] = customer.email
        request['phoneDay'] = customer.home_phone
        request['phoneEvening'] = customer.work_phone
        request['phoneMobile'] = customer.mobile_phone
        request['fax'] = customer.fax
        request['title'] = customer.title
        request['department'] = customer.department
        request = self._build_address(request, customer.address)

        return request

    def _build_payment_method(self, request, payment, transaction_type):
        if payment is None:
            return request

        request['preferredPayment'] = payment.preferred_payment
        request['paymentMethodIdentifier'] = payment.id
        request['customerKey'] = payment.customer_key
        request['nameOnAccount'] = payment.name_on_account
        request = self._build_address(request, payment.address)

        if transaction_type == TransactionType.Create:
            has_token, token_value = self._has_token(payment.paymentMethod)
            payment_info = None
            payment_info_key = None

            if isinstance(payment.payment_method, CardData):
                method = payment.payment_method
                payment_info_key = 'alternateIdentity' if has_token else 'card'
                payment_info = {
                    'token' if has_token else 'number':
                    token_value if has_token else method.number,
                    'expMon':
                    method.exp_month,
                    'expYear':
                    method.exp_year,
                }

                if has_token:
                    payment_info['type'] = 'SINGLEUSETOKEN'

                request['cardVerificationValue'] = method.cvn
            elif isinstance(payment.payment_method, TrackData):
                method = payment.payment_method
                payment_info_key = 'track'
                payment_info = {
                    'data': method.value,
                    'dataEntryMode': method.entry_method.upper(),
                }

            if isinstance(payment.payment_method, ECheck):
                check = payment.payment_method
                request['achType'] = self._map_account_type(check.account_type)
                request['accountType'] = self._map_check_type(check.check_type)
                request['telephoneIndicator'] = False \
                    if check.sec_code == SecCode.CCD or check.sec_code == SecCode.PPD \
                    else True
                request['routingNumber'] = check.routing_number
                request['accountNumber'] = check.account_number
                request['accountHolderYob'] = check.birth_year
                request['driversLicenseState'] = check.drivers_license_state
                request['driversLicenseNumber'] = check.drivers_license_number
                request['socialSecurityNumberLast4'] = check.ssn_last_4
                request.pop('country', None)

            if isinstance(payment.payment_method, Encryptable):
                enc = payment.payment_method.encryption_data

                if enc is not None:
                    payment_info['trackNumber'] = enc.track_number
                    payment_info['key'] = enc.ktb
                    payment_info['encryptionType'] = 'E3'

        else:  # EDIT FIELDS
            request.pop('customerKey', None)
            request['paymentStatus'] = payment.status
            request['cpcTaxType'] = payment.tax_type
            request['expirationDate'] = payment.expiration_date

        if payment_info is not None:
            request[payment_info_key] = payment_info

        return request

    def _map_account_type(self, account_type):
        if account_type == AccountType.Checking:
            return 'Checking'

        if account_type == AccountType.Savings:
            return 'Savings'

        return None

    def _map_check_type(self, check_type):
        if check_type == CheckType.Personal:
            return 'Personal'

        if check_type == CheckType.Business:
            return 'Business'

        return None

    def _build_schedule(self, request, schedule, transaction_type):
        if schedule is None:
            return request

        request['scheduleIdentifier'] = schedule.id
        request['scheduleName'] = schedule.name
        request['scheduleStatus'] = schedule.status
        request['paymentMethodKey'] = schedule.payment_key
        request = self._build_amount(request, 'subtotalAmount',
                                     schedule.amount, schedule.currency,
                                     transaction_type)
        request = self._build_amount(request, 'taxAmount', schedule.tax_amount,
                                     schedule.currency, transaction_type)
        request['deviceId'] = schedule.device_id
        request['processingDateInfo'] = self._map_processing_date(schedule)
        request = self._build_date(request, 'endDate', schedule.end_date,
                                   (transaction_type == TransactionType.Edit))
        request['reprocessingCount'] = schedule.reprocessing_count or 3
        request['emailReceipt'] = schedule.email_receipt
        request[
            'emailAdvanceNotice'] = 'Yes' if schedule.email_notification else 'No'
        # debt repay ind
        request['invoiceNbr'] = schedule.invoice_number
        request['poNumber'] = schedule.po_number
        request['description'] = schedule.description
        request['numberOfPayments'] = schedule.number_of_payments

        if transaction_type == TransactionType.Create:
            request['customerKey'] = schedule.customer_key
            request = self._build_date(request, 'startDate',
                                       schedule.start_date)
            request['frequency'] = schedule.frequency
            request['duration'] = self._map_duration(schedule)
        else:  # Edit Fields
            if not schedule.has_started:
                request = self._build_date(request, 'startDate',
                                           schedule.start_date)
                request['frequency'] = schedule.frequency
                request['duration'] = self._map_duration(schedule)
            else:
                request = self._build_date(request, 'cancellationDate',
                                           schedule.cancellation_date)
                request = self._build_date(request, 'nextProcressingDate',
                                           schedule.next_processing_date)

        return request

    def _map_duration(self, schedule):
        if schedule.number_of_payments is not None:
            return 'Limited Number'

        if schedule.end_date is not None:
            return 'End Date'

        return 'Ongoing'

    def _map_processing_date(self, schedule):
        frequencies = ['Monthly', 'Bi-Monthly', 'Quarterly', 'Semi-Annually']

        if schedule.frequency in frequencies:
            if schedule.payment_schedule == PaymentSchedule.FirstDayOfTheMonth:
                return 'First'

            if schedule.payment_schedule == PaymentSchedule.LastDayOfTheMonth:
                return 'Last'

            day = schedule.start_date  # TODO: get date number
            return 'Last' if day > 28 else day

        if schedule.frequency == 'Semi-Monthly':
            return 'Last' \
                if schedule.payment_schedule == PaymentSchedule.LastDayOfTheMonth \
                else 'First'

        return None

    def _build_date(self, request, name, date, force=False):
        if date is not None or force is True:
            # TODO: format date
            value = date.value if date.value is not None else None
            request[name] = value

        return request

    def _build_amount(self, request, name, amount, currency, transaction_type):
        if amount is not None:
            request[name] = {
                # TODO: format in cents
                'value': amount,
            }

            if transaction_type == TransactionType.Create:
                request[name]['currency'] = currency

        return request

    def _build_address(self, request, address):
        if address is not None:
            request['addressLine1'] = address.street_address_1
            request['addressLine2'] = address.street_address_2
            request['city'] = address.city
            request['country'] = address.country
            request['stateProvince'] = address.state
            request['zipPostalCode'] = address.postal_code

        return request

    def _hydrate_customer(self, response):
        customer = Customer()

        customer.key = response['customerKey']
        customer.id = response['customerIdentifier']
        customer.first_name = response['firstName']
        customer.last_name = response['lastName']
        customer.company = response['company']
        customer.status = response['customerStatus']
        customer.title = response['title']
        customer.department = response['department']
        customer.email = response['primaryEmail']
        customer.home_phone = response['phoneEvening']
        customer.work_phone = response['phoneDay']
        customer.mobile_phone = response['phoneMobile']
        customer.fax = response['fax']
        customer.address = Address()
        customer.address.street_address_1 = response['addressLine1']
        customer.address.street_address_2 = response['addressLine2']
        customer.address.city = response['city']
        customer.address.province = response['stateProvince']
        customer.address.postal_code = response['zipPostalCode']
        customer.country = response['country']

        return customer

    def _hydrate_payment_method(self, response):
        method = RecurringPaymentMethod()

        method.key = response['paymentMethodKey']
        method.id = response['paymentMethodIdentifier']
        method.payment_type = response['paymentMethodType']
        method.preferred_payment = response['preferredPayment'] == 'true'
        method.status = response['paymentStatus']
        method.customer_key = response['customerKey']
        method.name_on_account = response['nameOnAccount']
        method.commercial_indicator = response['commercialIndicator']
        method.tax_type = response['taxType']
        method.expiration_date = response['expirationDate']
        method.address = Address()
        method.address.street_address_1 = response['addressLine1']
        method.address.street_address_2 = response['addressLine2']
        method.address.city = response['city']
        method.address.province = response['stateProvince']
        method.address.postal_code = response['zipPostalCode']
        method.country = response['country']

        return method

    def _hydrate_schedule(self, response):
        schedule = Schedule()

        schedule.key = response['scheduleKey']
        schedule.id = response['scheduleIdentifier']
        schedule.customer_key = response['customerKey']
        schedule.name = response['scheduleName']
        schedule.status = response['scheduleStatus']
        schedule.payment_key = response['paymentMethodKey']

        if response['subtotalAmount'] is not None:
            subtotal = response['subtotalAmount']
            schedule.amount = subtotal['value']
            schedule.currency = subtotal['currency']

        if response['taxAmount'] is not None:
            tax = response['taxAmount']
            schedule.tax_amount = tax['value']

        schedule.device_id = response['deviceId']
        schedule.start_date = response['startDate']

        if response['processingDateInfo'] is None:
            schedule.payment_schedule = PaymentSchedule.Dynamic
        else:
            if response['processingDateInfo'] == 'Last':
                schedule.payment_schedule = PaymentSchedule.LastDayOfTheMonth
            elif response['processingDateInfo'] == 'First':
                schedule.payment_schedule = PaymentSchedule.FirstDayOfTheMonth
            else:
                schedule.payment_schedule = PaymentSchedule.Dynamic

        schedule.frequency = response['frequency']
        schedule.end_date = response['endDate']
        schedule.reprocessing_count = response['reprocessingCount']
        schedule.email_receipt = response['emailReceipt']
        schedule.email_notification = response['emailNotification'] == 'Yes'
        schedule.invoice_number = response['invoiceNbr']
        schedule.po_number = response['poNumber']
        schedule.description = response['description']
        # statusSetDate
        schedule.next_processing_date = response['nextProcessingDate']
        # previousProcessingDate
        # approvedTransactionCount
        # failureCount
        # totalApprovedAmountToDate
        # numberOfPaymentsRemaining
        schedule.cancellation_date = response['cancellationDate']
        # creationDate
        schedule.has_started = response['scheduleStarted'] == 'true'

        return schedule

    def _has_token(self, payment_method):
        if isinstance(payment_method,
                      Tokenizable) and payment_method.token is not None:
            return True, payment_method.token
        return False, None


class PorticoConnector(XmlGateway):
    site_id = None
    license_id = None
    device_id = None
    username = None
    password = None
    secret_api_key = None
    developer_id = None
    version_number = None

    @property
    def supports_hosted_payments(self):
        return False

    def __init__(self):
        XmlGateway.__init__(self)

    def process_authorization(self, builder):
        transaction = et.Element(self._map_transaction_type(builder))
        block1 = et.SubElement(transaction, 'Block1')

        # build request
        if (builder.transaction_type == TransactionType.Sale
                or builder.transaction_type == TransactionType.Auth
                or builder.transaction_type == TransactionType.Refund):
            if (builder.payment_method.payment_method_type !=
                    PaymentMethodType.Gift
                    and builder.payment_method.payment_method_type !=
                    PaymentMethodType.ACH):
                et.SubElement(
                    block1,
                    'AllowDup').text = 'Y' if builder.allow_duplicates else 'N'
                if (builder.transaction_type != TransactionType.Refund
                        and (builder.transaction_modifier ==
                             TransactionModifier.NoModifier
                             or not builder.transaction_modifier)
                        and builder.payment_method.payment_method_type !=
                        PaymentMethodType.EBT
                        and builder.payment_method.payment_method_type !=
                        PaymentMethodType.Recurring):
                    et.SubElement(block1, 'AllowPartialAuth').text = \
                        'Y' if builder.allow_partial_auth else 'N'

        if builder.amount is not None:
            et.SubElement(block1, 'Amt').text = str(builder.amount)

        if builder.gratuity:
            et.SubElement(block1, 'GratuityAmtInfo').text = str(
                builder.gratuity)

        if builder.convenience_amt:
            et.SubElement(block1, 'ConvenienceAmtInfo').text = str(
                builder.convenience_amt)

        if builder.shipping_amt:
            et.SubElement(block1, 'ShippingAmtInfo').text = str(
                builder.shipping_amt)

        # because plano
        if builder.cash_back_amount is not None:
            et.SubElement(
                block1,
                'CashbackAmtInfo' \
                    if builder.payment_method.payment_method_type == PaymentMethodType.Debit \
                    else 'CashBackAmount'
            ).text = str(builder.cash_back_amount)

        # offline auth code
        if builder.offline_auth_code:
            et.SubElement(block1,
                          'OfflineAuthCode').text = builder.offline_auth_code

        # alias action
        if builder.transaction_type == TransactionType.Alias:
            et.SubElement(block1, 'Action').text = builder.alias_action.value
            et.SubElement(block1, 'Alias').text = builder.alias

        # card holder
        is_check = builder.payment_method.payment_method_type == PaymentMethodType.ACH
        if is_check or builder.billing_address is not None:
            holder = et.SubElement(block1, 'ConsumerInfo'
                                   if is_check else 'CardHolderData')

            if builder.billing_address is not None:
                et.SubElement(holder, 'Address1'
                              if is_check else 'CardHolderAddr'
                              ).text = builder.billing_address.street_address_1
                et.SubElement(
                    holder, 'City' if is_check else
                    'CardHolderCity').text = builder.billing_address.city
                et.SubElement(
                    holder, 'State' if is_check else 'CardHolderState'
                ).text = builder.billing_address.province or builder.billing_address.state
                et.SubElement(
                    holder, 'Zip' if is_check else
                    'CardHolderZip').text = builder.billing_address.postal_code

            if is_check:
                check = builder.payment_method

                if check.check_holder_name is not None:
                    names = check.check_holder_name.split(' ', 2)
                    et.SubElement(holder, 'FirstName').text = names[0]
                    et.SubElement(holder, 'LastName').text = names[1]

                et.SubElement(holder, 'CheckName').text = check.check_name
                et.SubElement(holder, 'PhoneNumber').text = check.phone_number
                et.SubElement(holder,
                              'DLNumber').text = check.drivers_license_number
                et.SubElement(holder,
                              'DLState').text = check.drivers_license_state

                if check.ssn_last_4 is not None or check.birth_year is not None:
                    identity = et.SubElement(holder, 'IdentityInfo')
                    et.SubElement(identity, 'SSNL4').text = check.ssn_last_4
                    et.SubElement(identity, 'DOBYear').text = check.birth_year

        # card data
        has_token, token_value = self._has_token(builder.payment_method)

        # because debit
        card_data = None
        if (builder.payment_method.payment_method_type ==
                PaymentMethodType.Debit
                or builder.payment_method.payment_method_type ==
                PaymentMethodType.ACH):
            card_data = block1
        else:
            card_data = et.Element('CardData')

        if self._has_attr(
                builder.payment_method,
                'is_card_data') and builder.payment_method.is_card_data:
            card = builder.payment_method

            manual_entry = et.SubElement(card_data, 'TokenData'
                                         if has_token else 'ManualEntry')
            et.SubElement(manual_entry, 'TokenValue' if has_token else
                          'CardNbr').text = token_value or card.number

            et.SubElement(manual_entry, 'ExpMonth').text = card.exp_month
            et.SubElement(manual_entry, 'ExpYear').text = card.exp_year
            et.SubElement(manual_entry, 'CVV2').text = card.cvn
            et.SubElement(
                manual_entry,
                'ReaderPresent').text = 'Y' if card.reader_present else 'N'
            et.SubElement(
                manual_entry,
                'CardPresent').text = 'Y' if card.card_present else 'N'
            block1.append(card_data)

            if isinstance(card, CreditCardData):
                secure_ecom = card.three_d_secure

                if secure_ecom is not None:
                    secure_ecommerce = et.SubElement(block1, 'SecureECommerce')
                    et.SubElement(secure_ecommerce, 'PaymentDataSource'
                                  ).text = secure_ecom.payment_data_source
                    et.SubElement(secure_ecommerce, 'TypeOfPaymentData'
                                  ).text = secure_ecom.payment_data_type
                    et.SubElement(secure_ecommerce,
                                  'PaymentData').text = secure_ecom.cavv
                    et.SubElement(secure_ecommerce,
                                  'ECommerceIndicator').text = secure_ecom.eci
                    et.SubElement(secure_ecommerce,
                                  'XID').text = secure_ecom.xid

            if builder.transaction_modifier == TransactionModifier.Recurring:
                recurring = et.SubElement(block1, 'RecurringData')
                et.SubElement(recurring,
                              'ScheduleID').text = builder.schedule_id
                et.SubElement(
                    recurring,
                    'OneTime').text = 'Y' if builder.one_time_payment else 'N'

        elif self._has_attr(
                builder.payment_method,
                'is_track_data') and builder.payment_method.is_track_data:
            track = builder.payment_method

            track_data = et.SubElement(card_data, 'TokenData'
                                       if has_token else 'TrackData')
            if not has_token:
                track_data.text = str(track.value)
                track_data.set('method', 'proximity'
                               if self._has_attr(track, 'entry_method')
                               and track.entry_method == EntryMethod.Proximity
                               else 'swipe')

                # if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                #     if builder.tag_data is not None:
                #         tag_data = et.SubElement(block1, 'EMVData')
                #         et.SubElement(tag_data, 'EMVTagData').text = builder.tag_data

                # if builder.payment_method.payment_method_type == PaymentMethodType.Debit:
                #     chip_condition = None
                #     if builder.chip_condition is not None:
                #         chip_condition = 'CHIP_FAILED_PREV_SUCCESS' \
                #             if builder.chip_condition == EmvChipCondition.ChipFailedPreviousSuccess \
                #             else 'CHIP_FAILED_PREV_FAILED'

                #     et.SubElement(block1, 'AccountType').text = builder.account_type
                #     et.SubElement(block1, 'EMVChipCondition').text = chip_condition
                #     et.SubElement(block1, 'MessageAuthenticationCode').text = \
                #         builder.message_authentication_code
                #     et.SubElement(block1, 'PosSequenceNbr').text = builder.pos_sequence_number
                #     et.SubElement(block1, 'ReversalReasonCode').text = builder.reversal_reason_code

                #     if builder.tag_data is not None:
                #         tag_data = et.SubElement(block1, 'TagData')
                #         et.SubElement(tag_data, 'TagValues', {'source': 'chip'}).text = builder.tag_data
                # else:
                if track.payment_method_type != PaymentMethodType.Debit:
                    block1.append(card_data)
            else:
                et.SubElement(track_data, 'TokenValue').text = token_value

        elif isinstance(builder.payment_method, GiftCard):
            card = builder.payment_method

            # currency
            if builder.currency:
                et.SubElement(block1,
                              'Currency').text = builder.currency.upper()

            # if it's replace, add the new card, and change the card data name to be old card data
            if builder.transaction_type == TransactionType.Replace:
                new_card_data = et.SubElement(block1, 'NewCardData')
                et.SubElement(new_card_data, builder.replacement_card.value_type).text = \
                    builder.replacement_card.value
                if builder.replacement_card.pin:
                    et.SubElement(new_card_data,
                                  'PIN').text = builder.replacement_card.pin

                card_data = et.Element('OldCardData')

            et.SubElement(card_data, card.value_type).text = card.value
            if card.pin:
                et.SubElement(card_data, 'PIN').text = card.pin

            if builder.alias_action != AliasAction.Create:
                block1.append(card_data)

        elif isinstance(builder.payment_method, ECheck):
            check = builder.payment_method

            # check action
            et.SubElement(block1, 'CheckAction').text = 'SALE'

            # account info
            if not has_token:
                account_info = et.SubElement(block1, 'AccountInfo')
                if check.routing_number:
                    et.SubElement(account_info,
                                  'RoutingNumber').text = check.routing_number
                if check.account_number:
                    et.SubElement(account_info,
                                  'AccountNumber').text = check.account_number
                if check.check_number:
                    et.SubElement(account_info,
                                  'CheckNumber').text = check.check_number
                if check.micr_number:
                    et.SubElement(account_info,
                                  'MICRData').text = check.micr_number
                if check.account_type:
                    et.SubElement(
                        account_info,
                        'AccountType').text = check.account_type.value
            else:
                et.SubElement(block1, 'TokenValue').text = token_value

            if check.entry_mode:
                et.SubElement(
                    block1,
                    'DataEntryMode').text = check.entry_mode.value.upper()
            if check.check_type:
                et.SubElement(block1,
                              'CheckType').text = check.check_type.value
            if check.sec_code:
                et.SubElement(block1, 'SECCode').text = check.sec_code.value

            # verify info
            verify = et.SubElement(block1, 'VerifyInfo')
            et.SubElement(
                verify,
                'CheckVerify').text = 'Y' if check.check_verify else 'N'
            et.SubElement(verify,
                          'ACHVerify').text = 'Y' if check.ach_verify else 'N'

        if isinstance(builder.payment_method, TransactionReference):
            reference = builder.payment_method
            et.SubElement(block1,
                          'GatewayTxnId').text = reference.transaction_id
            if reference.client_transaction_id:
                et.SubElement(
                    block1,
                    'ClientTxnId').text = reference.client_transaction_id

        if isinstance(builder.payment_method, RecurringPaymentMethod):
            method = builder.payment_method

            # check action
            if method.payment_type == 'ACH':
                block1.remove('AllowDup')
                et.SubElement(block1, 'CheckAction').text = 'SALE'

            # payment method stuff
            et.SubElement(block1, 'PaymentMethodKey').text = method.key
            if (method.payment_method is not None
                    and isinstance(method.payment_method, CreditCardData)):
                card = method.payment_method
                data = et.SubElement(block1, 'PaymentMethodKeyData')
                et.SubElement(data, 'ExpMonth').text = card.exp_month
                et.SubElement(data, 'ExpYear').text = card.exp_year
                et.SubElement(data, 'CVV2').text = card.cvn

            # recurring data
            recurring = et.SubElement(block1, 'RecurringData')
            et.SubElement(recurring, 'ScheduleID').text = builder.schedule_id
            et.SubElement(
                recurring,
                'OneTime').text = 'Y' if builder.one_time_payment else 'N'

        # pin block
        if self._has_attr(builder.payment_method, 'pin_block'):
            if builder.transaction_type != TransactionType.Reversal:
                et.SubElement(
                    block1, 'PinBlock').text = builder.payment_method.pin_block

        # encryption
        if self._has_attr(builder.payment_method, 'encryption_data'):
            encryption_data = builder.payment_method.encryption_data

            if encryption_data is not None:
                enc = et.SubElement(card_data, 'EncryptionData')
                if encryption_data.version:
                    et.SubElement(enc,
                                  'Version').text = encryption_data.version
                if encryption_data.track_number:
                    et.SubElement(enc, 'EncryptedTrackNumber'
                                  ).text = encryption_data.track_number
                if encryption_data.ktb:
                    et.SubElement(enc, 'KTB').text = encryption_data.ktb
                if encryption_data.ktb:
                    et.SubElement(enc, 'KSN').text = encryption_data.ksn

        # set token flag
        if self._has_attr(
                builder.payment_method,
                'tokenizable') and builder.payment_method.tokenizable:
            et.SubElement(card_data, 'TokenRequest').text = \
                'Y' if builder.request_multi_use_token else 'N'

        # balance inquiry type
        if self._has_attr(builder, 'balance_inquiry_type'):
            et.SubElement(
                block1,
                'BalanceInquiryType').text = builder.balance_inquiry_type.value

        # cpc request
        if builder.level_2_request is not None:
            et.SubElement(block1, 'CPCReq').text = 'Y'

        # details
        if (builder.customer_id is not None or builder.description is not None
                or builder.invoice_number is not None):
            addons = et.SubElement(block1, 'AdditionalTxnFields')
            et.SubElement(addons, 'CustomerID').text = builder.customer_id
            et.SubElement(addons, 'Description').text = builder.description
            et.SubElement(addons, 'InvoiceNbr').text = builder.invoice_number

        # ecommerce info
        if builder.ecommerce_info is not None:
            et.SubElement(
                block1,
                'Ecommerce').text = builder.ecommerce_info.channel.value

            if (builder.invoice_number is not None
                    or builder.ecommerce_info.ship_month is not None):
                direct = et.SubElement(block1, 'DirectMktData')
                et.SubElement(
                    direct,
                    'DirectMktInvoiceNbr').text = builder.invoice_number
                et.SubElement(direct, 'DirectMktShipDay').text = str(
                    builder.ecommerce_info.ship_day)
                et.SubElement(direct, 'DirectMktShipMonth').text = str(
                    builder.ecommerce_info.ship_month)

        # dynamic descriptor
        if builder.dynamic_descriptor:
            et.SubElement(block1,
                          'TxnDescriptor').text = builder.dynamic_descriptor

        response = self.do_transaction(
            self._build_envelope(transaction, builder.client_transaction_id))
        return self._map_response(response, builder.payment_method)

    def serialize_request(self, _builder):
        raise UnsupportedTransactionException(
            'Portico does not support hosted payments.')

    def manage_transaction(self, builder):
        transaction = et.Element(self._map_transaction_type(builder))

        if builder.transaction_type != TransactionType.BatchClose:
            root = None

            if (builder.transaction_type == TransactionType.Reversal
                    or builder.transaction_type == TransactionType.Refund
                    or builder.payment_method.payment_method_type ==
                    PaymentMethodType.Gift
                    or builder.payment_method.payment_method_type ==
                    PaymentMethodType.ACH):
                root = et.SubElement(transaction, 'Block1')
            else:
                root = transaction

            # amount
            if builder.amount is not None:
                et.SubElement(root, 'Amt').text = str(builder.amount)

            # gratuity
            if builder.gratuity is not None:
                et.SubElement(root, 'GratuityAmtInfo').text = str(
                    builder.gratuity)

            # transaction id
            et.SubElement(root, 'GatewayTxnId').text = builder.transaction_id

            # client transaction id
            if builder.transaction_type == TransactionType.Reversal and builder.client_transaction_id:
                et.SubElement(
                    root, 'ClientTxnId').text = builder.client_transaction_id

            # cpc data
            if (builder.transaction_type == TransactionType.Edit
                    and builder.transaction_modifier ==
                    TransactionModifier.LevelII):
                cpc = et.SubElement(root, 'CPCData')
                if builder.po_number:
                    et.SubElement(cpc,
                                  'CardHolderPONbr').text = builder.po_number
                if builder.tax_type:
                    et.SubElement(cpc, 'TaxType').text = builder.tax_type.value
                if builder.tax_amount:
                    et.SubElement(cpc, 'TaxAmt').text = str(builder.tax_amount)

        response = self.do_transaction(
            self._build_envelope(transaction, builder.client_transaction_id))
        return self._map_response(response, builder.payment_method)

    def process_report(self, builder):
        transaction = et.Element(self._map_report_type(builder.report_type))
        if builder.timezone_conversion:
            et.SubElement(transaction,
                          'TzConversion').text = builder.timezone_conversion

        if isinstance(builder, gp.api.builders.TransactionReportBuilder):
            if builder.device_id:
                et.SubElement(transaction, 'DeviceId').text = builder.device_id

            if builder.start_date is not None:
                et.SubElement(transaction,
                              'RptStartUtcDT').text = builder.start_date

            if builder.end_date is not None:
                et.SubElement(transaction,
                              'RptEndUtcDT').text = builder.end_date

            if builder.transaction_id:
                et.SubElement(transaction,
                              'TxnId').text = builder.transaction_id

        response = self.do_transaction(self._build_envelope(transaction))
        return self._map_report_response(response, builder.report_type)

    def _build_envelope(self, transaction, client_transaction_id=None):
        envelope = et.Element(
            'soap:Envelope', {
                'xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            })
        body = et.SubElement(envelope, 'soap:Body')
        request = et.SubElement(body, 'PosRequest', {
            'xmlns': 'http://Hps.Exchange.PosGateway'
        })
        version1 = et.SubElement(request, 'Ver1.0')

        # header
        header = et.SubElement(version1, 'Header')
        if self.secret_api_key is not None:
            et.SubElement(header, 'SecretAPIKey').text = self.secret_api_key
        if self.site_id is not None:
            et.SubElement(header, 'SiteId').text = self.site_id
        if self.license_id is not None:
            et.SubElement(header, 'LicenseId').text = self.license_id
        if self.device_id is not None:
            et.SubElement(header, 'DeviceId').text = self.device_id
        if self.username is not None:
            et.SubElement(header, 'UserName').text = self.username
        if self.password is not None:
            et.SubElement(header, 'Password').text = self.password
        if self.developer_id is not None:
            et.SubElement(header, 'DeveloperID').text = self.developer_id
        if self.version_number is not None:
            et.SubElement(header, 'VersionNumber').text = self.version_number
        if client_transaction_id is not None:
            et.SubElement(header, 'ClientTxnId').text = client_transaction_id

        trans = et.SubElement(version1, 'Transaction')
        trans.append(transaction)

        return et.tostring(envelope)

    def _map_response(self, raw_response, payment_method):
        result = Transaction()

        namespaces = {
            'http://Hps.Exchange.PosGateway': None,
            'http://schemas.xmlsoap.org/soap/envelope/': None
        }
        root = xmltodict.parse(
            raw_response, process_namespaces=True,
            namespaces=namespaces)['Envelope']['Body']['PosResponse']['Ver1.0']
        accepted_codes = ['00', '0', '85', '10']

        header = root['Header']

        #  check gateway response
        gateway_rsp_code = self._normalize_response(header['GatewayRspCode'])
        gateway_rsp_text = header['GatewayRspMsg']

        if gateway_rsp_code not in accepted_codes:
            raise GatewayException(
                'Unexpected Gateway Response: {} - {}'.format(
                    gateway_rsp_code,
                    gateway_rsp_text), gateway_rsp_code, gateway_rsp_text)

        if 'Transaction' not in root:
            raise GatewayException('Unexpected Response: {} - {}'.format(
                gateway_rsp_code, gateway_rsp_text), gateway_rsp_code,
                                   gateway_rsp_text)

        items = list(root['Transaction'].items())
        item = items[0] if items[0] is not None else {}
        item = item[1] if item[1] is not None else item

        if 'AuthAmt' in item:
            result.authorized_amount = str(item['AuthAmt'])
        if 'AvailableBalance' in item:
            result.available_balance = str(item['AvailableBalance'])
        if 'AVSRsltCode' in item:
            result.avs_response_code = str(item['AVSRsltCode'])
        if 'AVSRsltText' in item:
            result.avs_response_message = str(item['AVSRsltText'])
        if 'BalanceAmt' in item:
            result.balance_amount = str(item['BalanceAmt'])
        if 'CardType' in item:
            result.card_type = str(item['CardType'])
        if 'TokenPANLast4' in item:
            result.card_last4 = str(item['TokenPANLast4'])
        if 'CAVVResultCode' in item:
            result.cavv_response_code = str(item['CAVVResultCode'])
        if 'CPCInd' in item:
            result.commercial_indicator = str(item['CPCInd'])
        if 'CVVRsltCode' in item:
            result.cvn_response_code = str(item['CVVRsltCode'])
        if 'CVVRsltText' in item:
            result.cvn_response_message = str(item['CVVRsltText'])
        if 'EMVIssuerResp' in item:
            result.emv_issuer_response = str(item['EMVIssuerResp'])
        if 'PointsBalanceAmt' in item:
            result.points_balance_amount = str(item['PointsBalanceAmt'])
        if 'RecurringDataCode' in item:
            result.recurring_data_code = str(item['RecurringDataCode'])
        if 'RefNbr' in item:
            result.reference_number = str(item['RefNbr'])
        result.response_code = gateway_rsp_code
        if 'RspCode' in item:
            result.response_code = self._normalize_response(
                str(item['RspCode']))
        result.response_message = gateway_rsp_text
        if 'RspText' in item:
            result.response_message = str(item['RspText'])
        elif 'RspMessage' in item:
            result.response_message = str(item['RspMessage'])
        if 'TxnDescriptor' in item:
            result.transaction_descriptor = str(item['TxnDescriptor'])
        if 'HostRspDT' in item:
            result.host_response_date = str(item['HostRspDT'])

        if payment_method is not None:
            result.transaction_reference = TransactionReference()
            result.transaction_reference.payment_method_type = payment_method.payment_method_type
            if 'GatewayTxnId' in header:
                result.transaction_reference.transaction_id = header[
                    'GatewayTxnId']
            if 'AuthCode' in item:
                result.transaction_reference.auth_code = item['AuthCode']

        # gift card create data
        if 'CardData' in item:
            result.gift_card = GiftCard()
            if 'CardNbr' in item['CardData']:
                result.gift_card.number = item['CardData']['CardNbr']
            if 'Alias' in item['CardData']:
                result.gift_card.alias = item['CardData']['Alias']
            if 'PIN' in item['CardData']:
                result.gift_card.pin = item['CardData']['PIN']

        # token data
        if 'TokenData' in header:
            if 'TokenValue' in header['TokenData']:
                result.token = header['TokenData']['TokenValue']

        # batch information
        if 'BatchId' in item:
            result.batch_summary = BatchSummary()
            result.batch_summary.id = item['BatchId']
            if 'TxnCnt' in item:
                result.batch_summary.transaction_count = item['TxnCnt']
            if 'TotalAmt' in item:
                result.batch_summary.total_amount = item['TotalAmt']
            if 'BatchSeqNbr' in item:
                result.batch_summary.sequence_number = item['BatchSeqNbr']

        # debit mac
        if 'DebitMac' in item:
            result.debit_mac = DebitMac()
            if 'TransactionCode' in item:
                result.debit_mac.transaction_code = item['TransactionCode']
            if 'TransmissionNumber' in item:
                result.debit_mac.transmission_number = item[
                    'TransmissionNumber']
            if 'BankResponseCode' in item:
                result.debit_mac.bank_response_code = item['BankResponseCode']
            if 'MacKey' in item:
                result.debit_mac.mac_key = item['MacKey']
            if 'PinKey' in item:
                result.debit_mac.pin_key = item['PinKey']
            if 'FieldKey' in item:
                result.debit_mac.field_key = item['FieldKey']
            if 'TraceNumber' in item:
                result.debit_mac.trace_number = item['TraceNumber']
            if 'MessageAuthenticationCode' in item:
                result.debit_mac.message_authentication_code = item[
                    'MessageAuthenticationCode']

        return result

    def _map_report_response(self, raw_response, report_type):
        namespaces = {
            'http://Hps.Exchange.PosGateway': None,
            'http://schemas.xmlsoap.org/soap/envelope/': None
        }
        root = xmltodict.parse(
            raw_response, process_namespaces=True, namespaces=namespaces)
        root = root['Envelope']['Body']['PosResponse']['Ver1.0']['Transaction']
        doc = root[self._map_report_type(report_type)]

        if report_type == ReportType.Activity and doc["Details"] is not None:
            response = []

            for value in doc["Details"]:
                response.append(self._hydrate_transaction_summary(value))

            return response

        if report_type == ReportType.TransactionDetail:
            return self._hydrate_transaction_summary(doc)

        return None

    @staticmethod
    def _normalize_response(original_response):
        if original_response == '0' or original_response == '85':
            return '00'
        return original_response

    @staticmethod
    def _map_transaction_type(builder):
        ret = None

        if builder.transaction_type == TransactionType.BatchClose:
            ret = 'BatchClose'
        elif builder.transaction_type == TransactionType.Decline:
            if builder.transaction_modifier == TransactionModifier.ChipDecline:
                ret = 'ChipCardDecline'
            elif builder.transaction_modifier == TransactionModifier.FraudDecline:
                ret = 'OverrideFraudDecline'
        elif builder.transaction_type == TransactionType.Verify:
            ret = 'CreditAccountVerify'
        elif builder.transaction_type == TransactionType.Capture:
            ret = 'CreditAddToBatch'
        elif builder.transaction_type == TransactionType.Auth:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                if builder.transaction_modifier == TransactionModifier.Additional:
                    ret = 'CreditAdditionalAuth'
                elif builder.transaction_modifier == TransactionModifier.Incremental:
                    ret = 'CreditIncrementalAuth'
                elif builder.transaction_modifier == TransactionModifier.Offline:
                    ret = 'CreditOfflineAuth'
                elif builder.transaction_modifier == TransactionModifier.Recurring:
                    ret = 'RecurringBillingAuth'
                else:
                    ret = 'CreditAuth'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Recurring:
                ret = 'RecurringBillingAuth'
        elif builder.transaction_type == TransactionType.Sale:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                if builder.transaction_modifier == TransactionModifier.Offline:
                    ret = 'CreditOfflineSale'
                elif builder.transaction_modifier == TransactionModifier.Recurring:
                    ret = 'RecurringBilling'
                else:
                    ret = 'CreditSale'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Recurring:
                if builder.payment_method.payment_type == 'ACH':
                    ret = 'CheckSale'
                else:
                    ret = 'RecurringBilling'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Debit:
                ret = 'DebitSale'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Cash:
                ret = 'CashSale'
            elif builder.payment_method.payment_method_type == PaymentMethodType.ACH:
                ret = 'CheckSale'
            elif builder.payment_method.payment_method_type == PaymentMethodType.EBT:
                if builder.transaction_modifier == TransactionModifier.CashBack:
                    ret = 'EBTCashBackPurchase'
                elif builder.transaction_modifier == TransactionModifier.Voucher:
                    ret = 'EBTVoucherPurchase'
                else:
                    ret = 'EBTFSPurchase'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Gift:
                ret = 'GiftCardSale'
        elif builder.transaction_type == TransactionType.Refund:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                ret = 'CreditReturn'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Debit:
                if isinstance(builder.payment_method, TransactionReference):
                    raise UnsupportedTransactionException()
                ret = 'DebitReturn'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Cash:
                ret = 'CashReturn'
            elif builder.payment_method.payment_method_type == PaymentMethodType.EBT:
                if isinstance(builder.payment_method, TransactionReference):
                    raise UnsupportedTransactionException()
                ret = 'EBTFSReturn'
        elif builder.transaction_type == TransactionType.Reversal:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                ret = 'CreditReversal'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Debit:
                if isinstance(builder.payment_method, TransactionReference):
                    raise UnsupportedTransactionException()
                ret = 'DebitReversal'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Gift:
                ret = 'GiftCardReversal'
        elif builder.transaction_type == TransactionType.Edit:
            if builder.transaction_modifier == TransactionModifier.LevelII:
                ret = 'CreditCPCEdit'
            else:
                ret = 'CreditTxnEdit'
        elif builder.transaction_type == TransactionType.Void:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                ret = 'CreditVoid'
            elif builder.payment_method.payment_method_type == PaymentMethodType.ACH:
                ret = 'CheckVoid'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Gift:
                ret = 'GiftCardVoid'
        elif builder.transaction_type == TransactionType.AddValue:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                ret = 'PrePaidAddValue'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Debit:
                ret = 'DebitAddValue'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Gift:
                ret = 'GiftCardAddValue'
        elif builder.transaction_type == TransactionType.Balance:
            if builder.payment_method.payment_method_type == PaymentMethodType.Credit:
                ret = 'PrePaidBalanceInquiry'
            elif builder.payment_method.payment_method_type == PaymentMethodType.EBT:
                ret = 'EBTBalanceInquiry'
            elif builder.payment_method.payment_method_type == PaymentMethodType.Gift:
                ret = 'GiftCardBalance'
        elif builder.transaction_type == TransactionType.BenefitWithdrawal:
            ret = 'EBTCashBenefitWithdrawal'
        elif builder.transaction_type == TransactionType.Activate:
            ret = 'GiftCardActivate'
        elif builder.transaction_type == TransactionType.Alias:
            ret = 'GiftCardAlias'
        elif builder.transaction_type == TransactionType.Deactivate:
            ret = 'GiftCardDeactivate'
        elif builder.transaction_type == TransactionType.Replace:
            ret = 'GiftCardReplace'
        elif builder.transaction_type == TransactionType.Reward:
            ret = 'GiftCardReward'

        if ret is None:
            raise UnsupportedTransactionException()

        return ret

    @staticmethod
    def _map_report_type(report_type):
        if report_type == ReportType.Activity:
            return 'ReportActivity'
        elif report_type == ReportType.TransactionDetail:
            return 'ReportTxnDetail'

        raise UnsupportedTransactionException()

    @staticmethod
    def _has_token(payment_method):
        if isinstance(payment_method,
                      Tokenizable) and payment_method.token is not None:
            return True, payment_method.token

        return False, None

    def _hydrate_transaction_summary(self, item):
        summary = TransactionSummary()

        if item is None:
            return summary

        if "Amt" in item:
            summary.amount = item["Amt"]

        if "AuthAmt" in item:
            summary.authorizated_amount = item["AuthAmt"]

        if "AuthCode" in item:
            summary.auth_code = item["AuthCode"]

        if "ClientTxnId" in item:
            summary.client_transaction_id = item["ClientTxnId"]

        if "DeviceId" in item:
            summary.device_id = item["DeviceId"]

        if "RspCode" in item or "IssuerRspCode" in item:
            summary.issuer_response_code = item[
                "RspCode"] if "RspCode" in item else item["IssuerRspCode"]

        if "RspText" in item or "IssuerRspText" in item:
            summary.issuer_response_message = item[
                "RspText"] if "RspText" in item else item["IssuerRspText"]

        if "MaskedCardNbr" in item:
            summary.masked_card_number = item["MaskedCardNbr"]

        if "OriginalGatewayTxnId" in item:
            summary.original_transaction_id = item["OriginalGatewayTxnId"]

        if "GatewayRspCode" in item:
            summary.gateway_response_code = self._normalize_response(
                item["GatewayRspCode"])

        if "GatewayResponseMsg" in item:
            summary.gateway_response_message = item["GatewayResponseMsg"]

        if "RefNbr" in item:
            summary.reference_number = item["RefNbr"]

        if "ServiceName" in item:
            summary.service_name = item["ServiceName"]

        if "SettlementAmt" in item:
            summary.settlement_amount = item["SettlementAmt"]

        if "TxnStatus" in item or "Status" in item:
            summary.status = item["TxnStatus"] \
                if "TxnStatus" in item \
                else item["Status"]

        if "TxnUtcDT" in item or "ReqUtcDT" in item:
            summary.transaction_date = item["TxnUtcDT"] \
                if "TxnUtcDT" in item \
                else item["ReqUtcDT"]

        if "GatewayTxnId" in item:
            summary.transaction_id = item["GatewayTxnId"]

        if "ConvenienceAmtInfo" in item:
            summary.convenience_amount = item["ConvenienceAmtInfo"]

        if "ShippingAmtInfo" in item:
            summary.shipping_amount = item["ShippingAmtInfo"]

        return summary

    def _has_attr(self, obj, attr):
        if not obj:
            return False

        try:
            return getattr(obj, attr)
        except AttributeError as _exc:
            return False


class RealexConnector(XmlGateway):
    merchant_id = None
    account_id = None
    shared_secret = None
    channel = None
    rebate_password = None
    refund_password = None
    hosted_payment_config = None

    @property
    def supports_hosted_payments(self):
        return True

    @property
    def supports_retrieval(self):
        return False

    @property
    def supports_update_payment_details(self):
        return True

    def process_authorization(self, builder):
        timestamp = builder.timestamp \
            if builder.timestamp \
            else GenerationUtils.generate_timestamp()
        order_id = builder.order_id \
            if builder.order_id \
            else GenerationUtils.generate_order_id()
        request_type = self._map_auth_request_type(builder)

        request = et.Element('request', {
            'timestamp': str(timestamp),
            'type': str(request_type),
        })

        et.SubElement(request, 'merchantid').text = self.merchant_id
        et.SubElement(request, 'account').text = self.account_id
        et.SubElement(request, 'channel').text = self.channel
        et.SubElement(request, 'orderid').text = order_id

        if builder.amount is not None:
            atts = {}
            if builder.currency:
                atts['currency'] = builder.currency
            et.SubElement(request, 'amount', atts).text = str(
                self.format_amount(builder.amount))

        if isinstance(builder.payment_method, CreditCardData):
            card = builder.payment_method

            card_element = et.SubElement(request, 'card')
            et.SubElement(card_element, 'number').text = card.number
            et.SubElement(card_element, 'expdate').text = card.short_expiry
            et.SubElement(card_element, 'chname').text = card.card_holder_name
            et.SubElement(card_element, 'type').text = card.card_type.upper()

            if card.cvn is not None:
                cvn_element = et.SubElement(card_element, 'cvn')
                et.SubElement(cvn_element, 'number').text = card.cvn
                if card.cvn_presence_indicator:
                    et.SubElement(cvn_element, 'presind').text = str(
                        card.cvn_presence_indicator.value)

            if card.three_d_secure is not None:
                mpi = et.SubElement(request, 'mpi')
                et.SubElement(mpi, 'cavv').text = card.three_d_secure.cavv
                et.SubElement(mpi, 'xid').text = card.three_d_secure.xid
                et.SubElement(mpi, 'eci').text = card.three_d_secure.eci

            to_hash = []
            if builder.transaction_type == TransactionType.Verify:
                to_hash = [
                    str(timestamp),
                    str(self.merchant_id),
                    str(order_id),
                    str(card.number)
                ]
            else:
                to_hash = [
                    str(timestamp),
                    str(self.merchant_id),
                    str(order_id),
                    str(self.format_amount(builder.amount))
                    if builder.amount else '',
                    str(builder.currency),
                    str(card.number)
                ]

            et.SubElement(request,
                          'sha1hash').text = GenerationUtils.generate_hash(
                              self.shared_secret, to_hash)

        if isinstance(builder.payment_method, RecurringPaymentMethod):
            recurring = builder.payment_method
            et.SubElement(request, 'payerref').text = recurring.customer_key
            et.SubElement(
                request, 'paymentmethod'
            ).text = recurring.key if recurring.key else recurring.id

            if builder.cvn is not None:
                payment_data = et.SubElement(request, 'paymentdata')
                cvn = et.SubElement(payment_data, 'cvn')
                et.SubElement(cvn, 'number').text = builder.cvn

            to_hash = []
            if builder.transaction_type == TransactionType.Verify:
                to_hash = [
                    str(timestamp),
                    str(self.merchant_id),
                    str(order_id),
                    str(recurring.customer_key)
                ]
            else:
                to_hash = [
                    str(timestamp),
                    str(self.merchant_id),
                    str(order_id),
                    str(self.format_amount(builder.amount))
                    if builder.amount else '',
                    str(builder.currency),
                    str(recurring.customer_key)
                ]

            et.SubElement(request,
                          'sha1hash').text = GenerationUtils.generate_hash(
                              self.shared_secret, to_hash)
        else:
            # TODO: token processing
            pass

        # refund hash
        if builder.transaction_type == TransactionType.Refund:
            refund_hash = GenerationUtils.generate_hash(self.refund_password)
            et.SubElement(
                request,
                'refundhash').text = refund_hash if refund_hash else ''

        if (builder.transaction_type == TransactionType.Sale
                or builder.transaction_type == TransactionType.Auth):
            auto_settle = '1' if builder.transaction_type == TransactionType.Sale else '0'
            et.SubElement(request, 'autosettle', {'flag': auto_settle})

        # TODO: needs to be multiple
        if builder.description is not None:
            comments = et.SubElement(request, 'comments')
            et.SubElement(comments, 'comment', {
                'id': '1'
            }).text = builder.description

        # recurring
        if builder.recurring_type is not None or builder.recurring_sequence is not None:
            et.SubElement(
                request, 'recurring', {
                    'type': str(builder.recurring_type.value).lower(),
                    'sequence': str(builder.recurring_sequence.value).lower(),
                })

        # tssinfo
        if (builder.customer_id is not None or builder.product_id is not None
                or builder.customer_ip_address is not None
                or builder.client_transaction_id is not None
                or builder.billing_address is not None
                or builder.shipping_address is not None):
            tss_info = et.SubElement(request, 'tssinfo')
            et.SubElement(tss_info, 'custnum').text = builder.customer_id
            et.SubElement(tss_info, 'prodid').text = builder.product_id
            et.SubElement(tss_info,
                          'varref').text = builder.client_transaction_id
            et.SubElement(tss_info,
                          'custipaddress').text = builder.customer_ip_address

            if builder.billing_address is not None:
                tss_info.append(self._build_address(builder.billing_address))

            if builder.shipping_address is not None:
                tss_info.append(self._build_address(builder.shipping_address))

        # et.SubElement(request, 'mobile')
        # et.SubElement(request, 'token').text = token

        response = self.do_transaction(et.tostring(request))
        return self._map_response(response,
                                  self._map_accepted_codes(request_type))

    def serialize_request(self, builder):
        if self.hosted_payment_config is None:
            raise ApiException(
                'Hosted configuration missing. Please check your configuration.'
            )

        encoder = lambda x: x \
            if self.hosted_payment_config.hpp_version == HppVersion.Version2 \
            else lambda x: base64.b64encode(bytearray(x.encode()))
        request = {}

        timestamp = builder.timestamp \
            if builder.timestamp \
            else GenerationUtils.generate_timestamp()
        order_id = builder.order_id \
            if builder.order_id \
            else GenerationUtils.generate_order_id()

        accepted_types = [
            TransactionType.Sale, TransactionType.Auth, TransactionType.Verify
        ]
        if builder.transaction_type not in accepted_types:
            raise UnsupportedTransactionException(
                'Only charge, authorize, and verify are supported through HPP.'
            )

        request['MERCHANT_ID'] = encoder(self.merchant_id)
        request['ACCOUNT'] = encoder(self.account_id)
        request['CHANNEL'] = encoder(self.channel)
        request['ORDER_ID'] = encoder(order_id)

        if builder.amount is not None:
            request['AMOUNT'] = encoder(self.format_amount(builder.amount))

        request['CURRENCY'] = encoder(builder.currency)
        request['TIMESTAMP'] = encoder(timestamp)
        request['AUTO_SETTLE_FLAG'] = encoder('1' \
            if builder.transaction_type == TransactionType.Sale \
            else '0')
        request['COMMENT1'] = encoder(builder.description)
        # request['COMMENT2'] =

        if self.hosted_payment_config.request_transaction_stability_score is not None:
            request['RETURN_TSS'] = encoder('1' \
                if self.hosted_payment_config.request_transaction_stability_score \
                else '0')

        if self.hosted_payment_config.dynamic_currency_conversion_enabled is not None:
            request['DCC_ENABLE'] = encoder('1' \
                if self.hosted_payment_config.dynamic_currency_conversion_enabled \
                else '0')

        if builder.hosted_payment_data is not None:
            request['CUST_NUM'] = encoder(
                builder.hosted_payment_data.customer_number)

            if (self.hosted_payment_config.display_saved_cards is not None
                    and builder.hosted_payment_data.customer_key is not None):
                request['HPP_SELECT_STORED_CARD'] = encoder(
                    builder.hosted_payment_data.customer_key)

            request['OFFER_SAVE_CARD'] = encoder('1' \
                if builder.hosted_payment_data.offer_to_save_card \
                else '0')
            request['PAYER_EXIST'] = encoder('1' \
                if builder.hosted_payment_data.customer_exists \
                else '0')

            if self.hosted_payment_config.display_saved_cards:
                request['PAYER_REF'] = encoder(
                    builder.hosted_payment_data.customer_key)

            request['PMT_REF'] = encoder(
                builder.hosted_payment_data.payment_key)
            request['PROD_ID'] = encoder(
                builder.hosted_payment_data.product_id)

        if builder.shipping_address is not None:
            request['SHIPPING_CODE'] = encoder(
                builder.shipping_address.postal_code)
            request['SHIPPING_CO'] = encoder(builder.shipping_address.country)

        if builder.billing_address is not None:
            request['BILLING_CODE'] = encoder(
                builder.billing_address.postal_code)
            request['BILLING_CO'] = encoder(builder.billing_address.country)

        request['CUST_NUM'] = encoder(builder.customer_id)
        request['VAR_REF'] = encoder(builder.client_transaction_id)
        request['HPP_LANG'] = encoder(self.hosted_payment_config.language)
        request['MERCHANT_RESPONSE_URL'] = encoder(
            self.hosted_payment_config.response_url)
        request['CARD_PAYMENT_BUTTON'] = encoder(
            self.hosted_payment_config.payment_button_text)

        if self.hosted_payment_config.card_storage_enabled is not None:
            request['CARD_STORAGE_ENABLE'] = encoder('1' \
                if self.hosted_payment_config.card_storage_enabled \
                else '0')

        if builder.transaction_type == TransactionType.Verify:
            request['VALIDATE_CARD_ONLY'] = encoder('1' \
                if builder.transaction_type == TransactionType.Verify \
                else '0')

        if self.hosted_payment_config.fraud_filter_mode != FraudFilterMode.NONE:
            request['HPP_FRAUDFILTER_MODE'] = encoder(
                self.hosted_payment_config.fraud_filter_mode)

        if builder.recurring_type is not None or builder.recurring_sequence is not None:
            request['RECURRING_TYPE'] = encoder(builder.recurring_type.lower())
            request['RECURRING_SEQUENCE'] = encoder(
                builder.recurring_sequence.lower())

        request['HPP_VERSION'] = encoder(self.hosted_payment_config.version)
        request['HPP_POST_DIMENSIONS'] = encoder(
            self.hosted_payment_config.post_dimensions)
        request['HPP_POST_RESPONSE'] = encoder(
            self.hosted_payment_config.post_response)

        to_hash = [
            str(timestamp),
            str(self.merchant_id),
            str(order_id),
            str(self.format_amount(builder.amount)) if builder.amount else '',
            str(builder.currency)
        ]

        if (self.hosted_payment_config.card_storage_enabled
                or (builder.hosted_payment_data is not None
                    and builder.hosted_payment_data.offer_to_save_card)
                or self.hosted_payment_config.display_saved_cards):
            to_hash.append(str(builder.hosted_payment_data.customer_key))
            to_hash.append(str(builder.hosted_payment_data.payment_key))

        if self.hosted_payment_config.fraud_filter_mode != FraudFilterMode.NONE:
            to_hash.append(str(self.hosted_payment_config.fraud_filter_mode))

        request['SHA1HASH'] = GenerationUtils.generate_hash(
            self.shared_secret, to_hash)
        return jsonpickle.encode(request)

    def manage_transaction(self, builder):
        timestamp = GenerationUtils.generate_timestamp()
        order_id = builder.order_id \
            if builder.order_id \
            else GenerationUtils.generate_order_id()
        request_type = self._map_manage_request_type(builder)

        request = et.Element('request', {
            'timestamp': str(timestamp),
            'type': str(request_type),
        })

        et.SubElement(request, 'merchantid').text = self.merchant_id
        et.SubElement(request, 'account').text = self.account_id
        et.SubElement(request, 'channel').text = self.channel
        et.SubElement(request, 'orderid').text = order_id
        et.SubElement(request, 'pasref').text = builder.transaction_id

        if builder.amount is not None:
            atts = {}
            if builder.currency:
                atts['currency'] = builder.currency
            et.SubElement(request, 'amount', atts).text = str(
                self.format_amount(builder.amount))
        elif builder.transaction_type == TransactionType.Capture:
            raise BuilderException('Amount cannot be null for Capture.')

        if builder.transaction_type == TransactionType.VerifySignature:
            et.SubElement(
                request, 'payres').text = builder.payer_authentication_response

        if builder.transaction_type == TransactionType.Refund:
            et.SubElement(request,
                          'authcode').text = builder.authorization_code
            refund_hash = GenerationUtils.generate_hash(self.rebate_password)
            et.SubElement(request, 'refundhash').text = \
                refund_hash if refund_hash else ''

        if builder.reason_code is not None:
            et.SubElement(request, 'reasoncode').text = builder.reason_code

        # TODO: needs to be multiple
        if builder.description is not None:
            comments = et.SubElement(request, 'comments')
            et.SubElement(comments, 'comment', {
                'id': '1'
            }).text = builder.description

        to_hash = [
            str(timestamp),
            str(self.merchant_id),
            str(order_id),
            str(self.format_amount(builder.amount)) if builder.amount else '',
            str(builder.currency) if builder.currency else '', ''
        ]
        et.SubElement(request,
                      'sha1hash').text = GenerationUtils.generate_hash(
                          self.shared_secret, to_hash)

        response = self.do_transaction(et.tostring(request))
        return self._map_response(response,
                                  self._map_accepted_codes(request_type))

    def process_report(self, _builder):
        raise UnsupportedTransactionException(
            'Reporting functionality is not supported through this gateway.')

    def process_recurring(self, builder):
        timestamp = GenerationUtils.generate_timestamp()
        order_id = builder.order_id \
            if builder.order_id \
            else GenerationUtils.generate_order_id()

        request = et.Element(
            'request', {
                'timestamp': str(timestamp),
                'type': self._map_recurring_request_type(builder),
            })

        et.SubElement(request, 'merchantid').text = self.merchant_id
        et.SubElement(request, 'account').text = self.account_id
        et.SubElement(request, 'orderid').text = order_id

        if (builder.transaction_type == TransactionType.Create
                or builder.transaction_type == TransactionType.Edit):
            if isinstance(builder.entity, Customer):
                customer = builder.entity
                request.append(self._build_customer(customer))
                to_hash = [
                    str(timestamp),
                    str(self.merchant_id),
                    str(order_id), '', '',
                    str(customer.key)
                ]
                et.SubElement(request,
                              'sha1hash').text = GenerationUtils.generate_hash(
                                  self.shared_secret, to_hash)

            if isinstance(builder.entity, RecurringPaymentMethod):
                payment = builder.entity
                card_element = et.SubElement(request, 'card')

                et.SubElement(
                    card_element,
                    'ref').text = payment.key if payment.key else payment.id
                et.SubElement(card_element,
                              'payerref').text = payment.customer_key

                if payment.payment_method is not None:
                    card = payment.payment_method
                    et.SubElement(card_element, 'number').text = card.number
                    et.SubElement(card_element,
                                  'expdate').text = card.short_expiry
                    et.SubElement(card_element,
                                  'chname').text = card.card_holder_name
                    et.SubElement(card_element, 'type').text = card.card_type

                    to_hash = []
                    if builder.transaction_type == TransactionType.Create:
                        to_hash = [
                            str(timestamp),
                            str(self.merchant_id),
                            str(order_id), '', '',
                            str(payment.customer_key),
                            str(card.card_holder_name),
                            str(card.number)
                        ]
                    else:
                        to_hash = [
                            str(timestamp),
                            str(self.merchant_id),
                            str(payment.customer_key),
                            str(payment.key if payment.key else payment.id),
                            str(card.short_expiry),
                            str(card.number if card.number else '')
                        ]

                    et.SubElement(
                        request,
                        'sha1hash').text = GenerationUtils.generate_hash(
                            self.shared_secret, to_hash)

        elif builder.transaction_type == TransactionType.Delete:
            if isinstance(builder.entity, RecurringPaymentMethod):
                payment = builder.entity
                card_element = et.SubElement(request, 'card')
                et.SubElement(
                    card_element,
                    'ref').text = payment.key if payment.key else payment.id
                et.SubElement(card_element,
                              'payerref').text = payment.customer_key

                to_hash = [
                    str(timestamp),
                    str(self.merchant_id),
                    str(payment.customer_key),
                    str(payment.key if payment.key else payment.id)
                ]
                et.SubElement(request,
                              'sha1hash').text = GenerationUtils.generate_hash(
                                  self.shared_secret, to_hash)

        response = self.do_transaction(et.tostring(request))
        return self._map_recurring_response(response, builder)

    def format_amount(self, amount):
        return int(float(amount) * 100)

    def _map_auth_request_type(self, builder):
        trans = builder.transaction_type
        payment = builder.payment_method

        if trans in [TransactionType.Sale, TransactionType.Auth]:
            if not isinstance(payment, Credit):
                return 'receipt-in'

            if builder.transaction_modifier == TransactionModifier.Offline:
                if payment is not None:
                    return 'manual'

                return 'offline'

            return 'auth'

        if trans == TransactionType.Capture:
            return 'settle'

        if trans == TransactionType.Verify:
            if isinstance(payment, Credit):
                return 'otb'

            if builder.transaction_modifier == TransactionModifier.Secure3D:
                return 'realvault-ed5-verify-enrolled'

            return 'receipt-in-otb'

        if trans == TransactionType.Refund:
            if isinstance(payment, Credit):
                return 'credit'

            return 'payment-out'

        if trans == TransactionType.VerifyEnrolled:
            return '3ds-verifyenrolled'

        raise UnsupportedTransactionException()

    def _map_manage_request_type(self, builder):
        trans = builder.transaction_type

        if trans == TransactionType.Capture:
            return 'settle'

        if trans == TransactionType.Hold:
            return 'hold'

        if trans == TransactionType.Refund:
            return 'rebate'

        if trans == TransactionType.Release:
            return 'release'

        if trans in [TransactionType.Void, TransactionType.Reversal]:
            return 'void'

        if trans == TransactionType.VerifySignature:
            return '3ds-verifysig'

        return 'unknown'

    def _map_recurring_request_type(self, builder):
        entity = builder.entity
        trans = builder.transaction_type

        if trans == TransactionType.Create:
            if isinstance(entity, Customer):
                return 'payer-new'

            if isinstance(entity, RecurringPaymentMethod):
                return 'card-new'

            raise UnsupportedTransactionException()

        if trans == TransactionType.Edit:
            if isinstance(entity, Customer):
                return 'payer-edit'

            if isinstance(entity, RecurringPaymentMethod):
                return 'card-update-card'

            raise UnsupportedTransactionException()

        if trans == TransactionType.Delete:
            if isinstance(entity, RecurringPaymentMethod):
                return 'card-cancel-card'

            raise UnsupportedTransactionException()

        raise UnsupportedTransactionException()

    def _map_response(self, response, accepted_codes=None):
        root = xmltodict.parse(response)['response']

        self._check_response(root, accepted_codes)

        result = Transaction()

        if 'result' in root:
            result.response_code = root['result']

        if 'message' in root:
            result.response_message = root['message']

        if 'cvnresult' in root:
            result.cvn_response_code = root['cvnresult']

        if 'avspostcoderesponse' in root:
            result.avs_response_code = root['avspostcoderesponse']

        if '@timestamp' in root:
            result.timestamp = root['@timestamp']

        result.transaction_reference = TransactionReference()

        if 'authcode' in root:
            result.transaction_reference.auth_code = root['authcode']

        if 'orderid' in root:
            result.transaction_reference.order_id = root['orderid']

        result.transaction_reference.payment_method_type = PaymentMethodType.Credit

        if 'pasref' in root:
            result.transaction_reference.transaction_id = root['pasref']

        if 'enrolled' in root:
            result.three_d_secure = ThreeDSecure()
            result.three_d_secure.enrolled = root['enrolled']
            result.three_d_secure.payer_authentication_response = root['pareq']
            result.three_d_secure.xid = root['xid']
            result.three_d_secure.issuer_acs_url = root['url']

        if 'threedsecure' in root:
            result.three_d_secure = ThreeDSecure()
            result.three_d_secure.status = root['status']
            result.three_d_secure.xid = root['xid']
            result.three_d_secure.cavv = root['cavv']

            if 'eci' in root and root['eci'] != '':
                result.three_d_secure.eci = root['eci']

            if 'algorithm' in root and root['algorithm'] != '':
                result.three_d_secure.algorithm = root['algorithm']

        return result

    def _map_accepted_codes(self, request_type):
        if request_type in ['3ds-verifysig', '3ds-verifyenrolled']:
            return ['00', '110']

        return ['00']

    def _map_recurring_response(self, response, builder):
        root = xmltodict.parse(response)

        self._check_response(root)

        return builder.entity

    def _check_response(self, root, accepted_codes=None):
        if accepted_codes is None:
            accepted_codes = ['00']

        if 'response' in root:
            root = root['response']

        response_code = root['result']
        response_message = root['message']

        if response_code not in accepted_codes:
            raise GatewayException(
                'Unexpected Gateway Response: {} - {}'.format(
                    response_code,
                    response_message), response_code, response_message)

    @staticmethod
    def _build_address(address):
        if address is None:
            return None

        code = address.postal_code

        if code is not None and code != '' and '|' not in code:
            code = '{}|{}'.format(code, address.street_address_1)
            if address.country == 'GB':
                code = '{}|{}'.format(
                    re.sub('[^0-9]', '', address.postal_code),
                    re.sub('[^0-9]', '', address.street_address_1))

        address_node = et.Element('address', {
            'type': 'billing' \
                if address.address_type == AddressType.Billing \
                else 'shipping'
        })
        et.SubElement(address_node, 'code').text = code
        et.SubElement(address_node, 'country').text = address.country

        return address_node

    @staticmethod
    def _build_customer(customer):
        payer = et.Element('payer')
        payer.set(
            'ref',
            customer.key \
                if customer.key \
                else GenerationUtils.generate_recurring_key()
        )

        et.SubElement(payer, 'title').text = customer.title
        et.SubElement(payer, 'firstname').text = customer.first_name
        et.SubElement(payer, 'surname').text = customer.last_name
        et.SubElement(payer, 'company').text = customer.company

        if customer.address is not None:
            address = et.SubElement(payer, 'address')

            et.SubElement(address,
                          "line1").text = customer.address.street_address_1
            et.SubElement(address,
                          "line2").text = customer.address.street_address_2
            et.SubElement(address,
                          "line3").text = customer.address.street_address_3
            et.SubElement(address, "city").text = customer.address.city
            et.SubElement(address, "county").text = customer.address.province
            et.SubElement(address,
                          "postcode").text = customer.address.postal_code

            country = et.SubElement(address, 'country')
            country.text = customer.address.country
            if country is not None:
                country.set('code', str(customer.address.country_code))

        phone = et.SubElement(payer, 'phonenumbers')
        et.SubElement(phone, "home").text = customer.home_phone
        et.SubElement(phone, "work").text = customer.work_phone
        et.SubElement(phone, "fax").text = customer.fax
        et.SubElement(phone, "mobile").text = customer.mobile_phone

        et.SubElement(payer, "email").text = customer.email

        return payer

    def _has_attr(self, obj, attr):
        if not obj:
            return False

        try:
            return getattr(obj, attr)
        except AttributeError as _exc:
            return False
