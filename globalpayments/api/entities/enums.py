from enum import Enum, IntEnum


class AliasAction(Enum):
    Create = 'CREATE'
    Add = 'ADD'
    Delete = 'DELETE'


class AddressType(Enum):
    """
    Indicates an address type.
    """

    #  Indicates a billing address.
    Billing = 0
    #  Indicates a shipping address.
    Shipping = 1


class DeviceType(Enum):
    """
    Indicates a device type for out of scope / semi-integrated devices.
    """

    #  Indicates a Pax S300 device.
    PAX_S300 = 0
    #  Indicates a HeartSIP iSC250 device.
    HSIP_ISC250 = 1


class ECommerceChannel(Enum):
    """
    Identifies eCommerce vs mail order / telephone order (MOTO) transactions.
    """
    #  Identifies eCommerce transactions.
    ECOM = 'ECOM'
    #  Identifies mail order / telephone order (MOTO) transactions.
    MOTO = 'MOTO'


class EmvChipCondition(Enum):
    """
    Indicates the chip condition for failed EMV chip reads
    """
    """
    Use this condition type when the current chip read failed but
    the previous transaction on the same device was either a
    successful chip read or was not a chip transaction.
    """
    ChipFailedPreviousSuccess = 0
    """
    Use this condition type when the current chip read failed and
    the previous transaction on the same device was also an
    unsuccessful chip read.
    """
    ChipFailedPreviousFailed = 1


class InquiryType(Enum):
    """
    Indicates an inquiry type.
    """

    Standard = "STANDARD"
    #  Indicates a foodstamp inquiry.
    FoodStamp = "FOODSTAMP"
    #  Indicates a cash inquiry.
    Cash = "CASH"
    Points = "POINTS"


class PaymentMethodType(IntEnum):
    """
    Indicates a payment method type.
    """
    """
    Indicates a payment method reference.
    Should be accompanied by a gateway transaction ID.
    """
    Reference = 0
    """
    Indicates a credit or PIN-less debit account.
    Should be accompanied by a token, card number, or track data.
    """
    Credit = 1 << 1
    """
    Indicates a PIN debit account.
    Should be accompanied by track data and a PIN block.
    """
    Debit = 1 << 2
    """
    Indicates an EBT account.
    Should be accompanied by track data and a PIN block.
    """
    EBT = 1 << 3
    """
    Indicates cash as the payment method.
    """
    Cash = 1 << 4
    """
    Indicates an ACH/eCheck account.
    Should be accompanied by a token or an account number and routing number.
    """
    ACH = 1 << 5
    """
    Indicates a gift/loyalty/stored value account.
    Should be accompanied by a token, card number, alias, or track data.
    """
    Gift = 1 << 6
    """
    Indicates a recurring payment method.
    Should be accompanied by a payment method key.
    """
    Recurring = 1 << 7


class EntryMethod(Enum):
    """
    Indicates how the payment method data was obtained.
    """

    #  Indicates manual entry.
    Manual = 'manual'
    #  Indicates swipe entry.
    Swipe = 'swipe'
    #  Indicates proximity/contactless entry.
    Proximity = 'proximity'


class GiftEntryMethod(Enum):
    """
    Indicates how the gift/loyalty/stored value account data was obtained.
    """

    #  Indicates swipe entry.
    Swipe = 0
    #  Indicates an alias was entered.
    Alias = 1
    #  Indicates manual entry.
    Manual = 2


class TransactionType(IntEnum):
    """
    Indicates the transaction type.
    """

    #  Indicates a decline.
    Decline = 0
    #  Indicates an account verify.
    Verify = 1 << 0
    #  Indicates a capture/add to batch
    Capture = 1 << 1
    #  Indicates an authorization without capture
    Auth = 1 << 2
    #  Indicates a refund
    Refund = 1 << 3
    #  Indicates a reversal
    Reversal = 1 << 4
    #  Indicates a sale/charge/auth with capture
    Sale = 1 << 5
    #  Indicates an edit
    Edit = 1 << 6
    #  Indicates a void
    Void = 1 << 7
    #  Indicates value should be added
    AddValue = 1 << 8
    #  Indicates a balance inquiry
    Balance = 1 << 9
    #  Indicates an activation
    Activate = 1 << 10
    #  Indicates an alias should be added
    Alias = 1 << 11
    #  Indicates the payment method should be replaced
    Replace = 1 << 12
    #  Indicates a reward
    Reward = 1 << 13
    #  Indicates a deactivation
    Deactivate = 1 << 14
    #  Indicates a batch close
    BatchClose = 1 << 15
    #  Indicates a resource should be created
    Create = 1 << 16
    #  Indicates a resource should be deleted
    Delete = 1 << 17
    #  Indicates a benefit withdrawal
    BenefitWithdrawal = 1 < 18
    #  Indicates a resource should be fetched
    Fetch = 1 << 19
    #  Indicates a resource type should be searched
    Search = 1 << 20
    #  Indicates a hold
    Hold = 1 << 21
    #  Indicates a release
    Release = 1 << 22
    #  Indicates a 3DSecure signature verification
    VerifySignature = 1 << 23
    #  Indicates a 3DSecure enrollment verification
    VerifyEnrolled = 1 << 24


class TransactionModifier(IntEnum):
    """
    Indicates if a transaction should be specialized.
    """

    #  Indicates no specialization
    NoModifier = 0
    #  Indicates an incremental transaction
    Incremental = 1 << 1
    #  Indicates an additional transaction
    Additional = 1 << 2
    #  Indicates an offline transaction
    Offline = 1 << 3
    #  Indicates a commercial request transaction
    LevelII = 1 << 4
    #  Indicates a fraud decline transaction
    FraudDecline = 1 << 5
    #  Indicates a chip decline transaction
    ChipDecline = 1 << 6
    #  Indicates a cash back transaction
    CashBack = 1 << 7
    #  Indicates a voucher transaction
    Voucher = 1 << 8
    #  Indicates a secure 3d transaction
    Secure3D = 1 << 9
    #  Indicates a hosted payment transaction
    HostedRequest = 1 << 10
    #  Indicates a recurring transaction
    Recurring = 1 << 11


class CvnPresenceIndicator(Enum):
    """
    Indicates CVN presence at time of payment.
    """

    #  Indicates
    Present = 1
    #  Indicates CVN was present but illegible
    Illegible = 2
    #  Indicates CVN was not present
    NotOnCard = 3
    #  Indicates was not requested
    NotRequested = 4


class TaxType(Enum):
    """
    Indicates the tax type.
    """

    #  Indicates tax was not used
    NotUsed = 'NOTUSED'
    #  Indicates sales tax was applied
    SalesTax = 'SALESTAX'
    #  Indicates tax exemption
    TaxExempt = 'TAXEXEMPT'


class CurrencyType(Enum):
    """
    Indicates the currency type.
    """

    #  Indicates true currency
    Currency = 'CURRENCY'
    #  Indicates loyalty points
    Points = 'POINTS'
    #  Indicates cash benefits
    CashBenefits = 'CASH_BENEFITS'
    #  Indicates food stamps
    FoodStamps = 'FOODSTAMPS'
    #  Indicates vouchers
    Voucher = 'VOUCHER'


class AccountType(Enum):
    """
    Indicates the account type for ACH/eCheck transactions.
    """

    #  Indicates a checking account
    Checking = 'CHECKING'
    #  Indicates a savings account
    Savings = 'SAVINGS'


class CheckType(Enum):
    """
    Indicates the check type for ACH/eCheck transactions.
    """

    #  indicates a personal check
    Personal = 'PERSONAL'
    #  Indicates a business check
    Business = 'BUSINESS'
    #  Indicates a payroll check
    Payroll = 'PAYROLL'


class SecCode(Enum):
    """
    Indicates the NACHA standard entry class (SEC) code for ACH/eCheck transactions.
    """

    #  Indicates prearranged payment and deposit (PPD)
    PPD = 'PPD'
    #  Indicates cash concentration or disbursement (CCD)
    CCD = 'CCD'
    #  Indicates point of purchase entry (POP)
    POP = 'POP'
    #  Indicates internet initiated entry (WEB)
    WEB = 'WEB'
    #  Indicates telephone initiated entry (TEL)
    TEL = 'TEL'
    #  Indicates verification only
    EBRONZE = 'EBRONZE'


class ReportType(IntEnum):
    """
    Indicates the report type.
    """

    #  Indicates a FindTransactions report
    FindTransactions = 0
    #  Indicates an Activity report
    Activity = 1 << 1
    #  Indicates a BatchDetail report
    BatchDetail = 1 << 2
    #  Indicates a BatchHistory report
    BatchHistory = 1 << 3
    #  Indicates a BatchSummary report
    BatchSummary = 1 << 4
    #  Indicates an OpenAuth report
    OpenAuths = 1 << 5
    #  Indicates a Search report
    Search = 1 << 6
    #  Indicates a TransactionDetail report
    TransactionDetail = 1 << 7


class TimeZoneConversion(Enum):
    """
    Indicates how timezones should be handled.
    """

    #  Indicates time is in coordinated universal time (UTC).
    UTC = 'UTC'
    #  Indicates the merchant is responsible for timezone conversions.
    Merchant = 'Merchant'
    #  Indicates the datacenter, gateway, or processor is responsible for timezone conversions.
    Datacenter = 'Datacenter'


class RecurringType(Enum):
    """
    Indicates the type of recurring schedule.
    """

    #  Indicates a fixed number of payments
    Fixed = 'Fixed'
    #  Indicates a variable number of payments.
    Variable = 'Variable'


class RecurringSequence(Enum):
    """
    Indicates when a transaction is ran in a recurring schedule.
    """

    #  Indicates the transaction is the first of a recurring schedule.
    First = 'First'
    #  Indicates the transaction is a subsequent payment of a recurring schedule.
    Subsequent = 'Subsequent'
    #  Indicates the transaction is the last of a recurring schedule.
    Last = 'Last'


class EmailReceipt(Enum):
    """
    Indicates when an email receipt should be sent for the transaction.
    Currently only used in recurring schedules.
    """

    #  Indicates an email receipt should never be sent.
    Never = 'Never'
    #  Indicates an email receipt should always be sent.
    All = 'All'
    #  Indicates an email receipt should only be sent on approvals.
    Approvals = 'Approvals'
    #  Indicates an email receipt should only be sent on declines.
    Declines = 'Declines'


class PaymentSchedule(Enum):
    """
    Indicates when in the month a recurring schedule should run.
    """

    #  Indicates a specified date.
    Dynamic = 'Dynamic'
    #  Indicates the first of the month.
    FirstDayOfTheMonth = 'FirstDayOfTheMonth'
    #  Indicates the last of the month.
    LastDayOfTheMonth = 'LastDayOfTheMonth'


class ScheduleFrequency(Enum):
    """
    Indicates the frequency of a recurring schedule.
    """

    #  Indicates a schedule should process payments weekly.
    Weekly = 'Weekly'
    #  Indicates a schedule should process payments bi-weekly (every other week).
    BiWeekly = 'Bi-Weekly'
    #  Indicates a schedule should process payments bi-monthly (twice a month).
    BiMonthly = 'Bi-Monthly'
    #  Indicates a schedule should process payments semi-monthly (every other month).
    SemiMonthly = 'Semi-Monthly'
    #  Indicates a schedule should process payments monthly.
    Monthly = 'Monthly'
    #  Indicates a schedule should process payments quarterly.
    Quarterly = 'Quarterly'
    #  Indicates a schedule should process payments semi-annually
    SemiAnnually = 'Semi-Annually'
    #  Indicates a schedule should process payments annually. (twice a year).
    Annually = 'Annually'


class ReasonCode(Enum):
    """
    Indicates a reason for the transaction.
    This is typically used for returns/reversals.
    """

    # Indicates fraud
    Fraud = 'FRAUD'
    # Indicates a false positive
    FalsePositive = 'FALSEPOSITIVE'
    # Indicates desired good is out of stock
    OutOfStock = 'OUTOFSTOCK'
    # Indicates desired good is in stock
    InStock = 'INSTOCK'
    # Indicates another reason
    Other = 'OTHER'
    # Indicates reason was not given
    NotGiven = 'NOTGIVEN'


class HppVersion(Enum):
    """
    Options when specifying HPP versions.
    Useful with `HostedPaymentConfig`.
    """

    #  HPP Version 1
    VERSION_1 = '1'
    #  HPP Version 2
    VERSION_2 = '2'


class FraudFilterMode(Enum):
    """
    Specify how the fraud filter should operate
    """

    #  Fraud filter will behave as configured in RealControl
    NONE = 0,
    #  Disables the fraud filter
    OFF = 1,
    #  Sets the fraud filter to passive mode
    PASSIVE = 2


class ReservationProviders(Enum):
    """
    Specifies the reservation service provider
    """
    FreshTxt = 1
