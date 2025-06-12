from enum import Enum, IntEnum
from typing import (
    Any,
)


class EnumWithValue(Enum):
    """Base Enum class that provides a `value` property for type-checking compatibility"""

    @property
    def value(self) -> Any:
        """Return the value of the enum member"""
        # This exists only for typing purposes - in Python 3, enum values
        # already have a .value attribute, but type checkers may not know this
        return super().value


class DocumentCategory(str, Enum):
    """Categories for documents in the system"""

    IdentityVerification = "IDENTITY_VERIFICATION"
    RiskReview = "RISK_REVIEW"
    Underwriting = "UNDERWRITING"


class FileType(str, Enum):
    """File types supported by the system"""

    TIF = "TIF"
    TIFF = "TIFF"
    PDF = "PDF"
    BMP = "BMP"
    JPEG = "JPEG"
    GIF = "GIF"
    PNG = "PNG"
    DOC = "DOC"
    DOCX = "DOCX"


class PaymentEntryMode(str, Enum):
    """
    Indicates the entry mode of a payment method.
    """

    MOTO = "MOTO"
    ECOM = "ECOM"
    IN_APP = "IN_APP"
    CHIP = "CHIP"
    SWIPE = "SWIPE"
    MANUAL = "MANUAL"
    CONTACTLESS_CHIP = "CONTACTLESS_CHIP"
    CONTACTLESS_SWIPE = "CONTACTLESS_SWIPE"
    PHONE = "PHONE"
    MAIL = "MAIL"


class AliasAction(Enum):
    Create = "CREATE"
    Add = "ADD"
    Delete = "DELETE"


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
    ECOM = "ECOM"
    #  Identifies mail order / telephone order (MOTO) transactions.
    MOTO = "MOTO"


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


class EmvLastChipRead(Enum):
    """
    Enumeration of EMV chip read status values.
    """

    SUCCESSFUL = "Successful"
    FAILED = "Failed"
    NOT_A_CHIP_TRANSACTION = "NotAChipTransaction"
    UNKNOWN = "Unknown"


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


class StoredCredentialInitiator(Enum):
    """
    Card Brand Stored Credentials.  used for COF
    """

    CardHolder = "C"
    Merchant = "M"
    Payer = "Payer"


class StoredCredentialReason(str, Enum):
    INCREMENTAL = "INCREMENTAL"
    RESUBMISSION = "RESUBMISSION"
    REAUTHORIZATION = "REAUTHORIZATION"
    DELAYED = "DELAYED"
    NO_SHOW = "NO_SHOW"


class StoredCredentialSequence(str, Enum):
    FIRST = "first"
    SUBSEQUENT = "subsequent"
    LAST = "last"


class StoredCredentialType(str, Enum):
    ONEOFF = "oneoff"
    INSTALLMENT = "installment"
    RECURRING = "recurring"
    UNSCHEDULED = "UNSCHEDULED"
    SUBSCRIPTION = "SUBSCRIPTION"
    MAINTAIN_PAYMENT_METHOD = "MAINTAIN_PAYMENT_METHOD"
    MAINTAIN_PAYMENT_VERIFICATION = "MAINTAIN_PAYMENT_VERIFICATION"
    ADD_PAYMENT_METHOD = "ADD_PAYMENT_METHOD"
    SPLIT_OR_DELAYED_SHIPMENT = "SPLIT_OR_DELAYED_SHIPMENT"
    TOP_UP = "TOP_UP"
    MAIL_ORDER = "MAIL_ORDER"
    TELEPHONE_ORDER = "TELEPHONE_ORDER"
    WHITELIST_STATUS_CHECK = "WHITELIST_STATUS_CHECK"
    OTHER_PAYMENT = "OTHER_PAYMENT"
    BILLING_AGREEMENT = "BILLING_AGREEMENT"


class TrackNumber(Enum):
    """Track number constants"""

    TRACK_ONE = "TRACK_ONE"
    TRACK_TWO = "TRACK_TWO"


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

    """
    Indicates an alternative payment method.
    """
    APM = 1 << 9

    """
    Indicates an account funds payment method.
    """
    AccountFunds = 1 << 10


class EntryMethod(Enum):
    """
    Indicates how the payment method data was obtained.
    """

    #  Indicates manual entry.
    Manual = "manual"
    #  Indicates swipe entry.
    Swipe = "swipe"
    #  Indicates proximity/contactless entry.
    Proximity = "proximity"


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


class AuthenticationSource(str, Enum):
    """
    Defines the sources of authentication for 3D Secure transactions.
    """

    Browser = "BROWSER"
    StoredRecurring = "STORED_RECURRING"
    MobileSdk = "MOBILE_SDK"
    MerchantInitiated = "MERCHANT_INITIATED"


class ColorDepth(Enum):
    ONE_BIT = "ONE_BIT"
    TWO_BITS = "TWO_BITS"
    FOUR_BITS = "FOUR_BITS"
    EIGHT_BITS = "EIGHT_BITS"
    FIFTEEN_BITS = "FIFTEEN_BITS"
    SIXTEEN_BITS = "SIXTEEN_BITS"
    TWENTY_FOUR_BITS = "TWENTY_FOUR_BITS"
    THIRTY_TWO_BITS = "THIRTY_TWO_BITS"
    FORTY_EIGHT_BITS = "FORTY_EIGHT_BITS"


class ChallengeWindowSize(Enum):
    WINDOWED_250X400 = "WINDOWED_250X400"
    WINDOWED_390X400 = "WINDOWED_390X400"
    WINDOWED_500X600 = "WINDOWED_500X600"
    WINDOWED_600X400 = "WINDOWED_600X400"
    FULL_SCREEN = "FULL_SCREEN"


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
    BenefitWithdrawal = 1 << 18  # Fixed typo in bit shift
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
    #  Indicates update Multi-Use Token
    TokenUpdate = 1 << 25
    #  Delete a Multi-Use Token
    TokenDelete = 1 << 26
    #  Indicates dispute acceptance
    DisputeAcceptance = 1 << 27
    #  Indicates dispute challenge
    DisputeChallenge = 1 << 28
    #  Indicates authentication initiation
    InitiateAuthentication = 1 << 29

    #  Indicates encrypted mobile transaction
    EncryptedMobile = 1 << 30
    #  Indicates decrypted mobile transaction
    DecryptedMobile = 1 << 31
    #  Indicates tokenize operation
    Tokenize = 1 << 32
    #  Indicates detokenize operation
    Detokenize = 1 << 33
    #  Indicates DCC rate lookup
    DccRateLookup = 1 << 34
    #  Indicates risk assessment
    RiskAssess = 1 << 35
    #  Indicates confirmation
    Confirm = 1 << 36
    #  Indicates reauthorization
    Reauth = 1 << 37

    # ProPay specific transactions
    #  ProPay: Create Account
    CreateAccount = 1 << 38
    #  ProPay: Edit Account
    EditAccount = 1 << 39
    #  ProPay: Reset Account Password
    ResetPassword = 1 << 40
    #  ProPay: Renew Account
    RenewAccount = 1 << 41
    #  ProPay: Update Beneficial Ownership Information
    UpdateBeneficialOwnership = 1 << 42
    #  ProPay: Disown an account
    DisownAccount = 1 << 43
    #  ProPay: Upload a document to a ProPay account related to a chargeback
    UploadDocumentChargeback = 1 << 44
    #  ProPay: Upload a document to a ProPay account
    UploadDocument = 1 << 45
    #  ProPay: Obtain a single-sign-on key
    ObtainSSOKey = 1 << 46
    #  ProPay: Update bank account ownership information
    UpdateBankAccountOwnership = 1 << 47
    #  ProPay: Add funds to a ProPay account (EFT)
    AddFunds = 1 << 48
    #  ProPay: Sweep funds from a ProPay account (EFT)
    SweepFunds = 1 << 49
    #  ProPay: Add a card for Flash Funds
    AddCardFlashFunds = 1 << 50
    #  ProPay: Move money out via Flash Funds
    PushMoneyFlashFunds = 1 << 51
    #  ProPay: Disburse funds to a ProPay account
    DisburseFunds = 1 << 52
    #  ProPay: SpendBack Transaction
    SpendBack = 1 << 53
    #  ProPay: Roll back a SplitPay transaction
    ReverseSplitPay = 1 << 54
    #  ProPay: Split funds from an existing transaction
    SplitFunds = 1 << 55
    #  ProPay: Get Account details
    GetAccountDetails = 1 << 56
    #  ProPay: Get Account balance
    GetAccountBalance = 1 << 57
    #  Site configuration
    SiteConfig = 1 << 58
    #  Time request
    TimeRequest = 1 << 59
    #  Get Token Information for the given token
    GetTokenInfo = 1 << 60
    #  PayLink update
    PayLinkUpdate = 1 << 61
    #  Order device
    OrderDevice = 1 << 62


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
    #  Indicates an alternative payment transaction
    AlternativePaymentMethod = 1 << 13
    #  Indicates an encrypted mobile transaction
    EncryptedMobile = 1 << 14
    #  Indicates an encrypted mobile transaction
    DecryptedMobile = 1 << 15


class EncyptedMobileType(Enum):
    """
    Enumeration of encrypted mobile payment types.
    """

    ApplePay = "apple-pay"
    GooglePay = "pay-with-google"
    ClickToPay = "click-to-pay"


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


class CardType(Enum):
    """
    Enumeration of supported credit/debit card types.
    """

    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    DISCOVER = "DISCOVER"
    AMEX = "AMEX"
    JCB = "JCB"
    DINERS = "DINERS"


class TaxType(Enum):
    """
    Indicates the tax type.
    """

    #  Indicates tax was not used
    NotUsed = "NOTUSED"
    #  Indicates sales tax was applied
    SalesTax = "SALESTAX"
    #  Indicates tax exemption
    TaxExempt = "TAXEXEMPT"


class CurrencyType(Enum):
    """
    Indicates the currency type.
    """

    #  Indicates true currency
    Currency = "CURRENCY"
    #  Indicates loyalty points
    Points = "POINTS"
    #  Indicates cash benefits
    CashBenefits = "CASH_BENEFITS"
    #  Indicates food stamps
    FoodStamps = "FOODSTAMPS"
    #  Indicates vouchers
    Voucher = "VOUCHER"


class AccountType(Enum):
    """
    Indicates the account type for ACH/eCheck transactions.
    """

    #  Indicates a checking account
    Checking = "CHECKING"
    #  Indicates a savings account
    Savings = "SAVINGS"
    Credit = "CREDIT"


class CheckType(Enum):
    """
    Indicates the check type for ACH/eCheck transactions.
    """

    #  indicates a personal check
    Personal = "PERSONAL"
    #  Indicates a business check
    Business = "BUSINESS"
    #  Indicates a payroll check
    Payroll = "PAYROLL"


class SecCode(Enum):
    """
    Indicates the NACHA standard entry class (SEC) code for ACH/eCheck transactions.
    """

    #  Indicates prearranged payment and deposit (PPD)
    PPD = "PPD"
    #  Indicates cash concentration or disbursement (CCD)
    CCD = "CCD"
    #  Indicates point of purchase entry (POP)
    POP = "POP"
    #  Indicates internet initiated entry (WEB)
    WEB = "WEB"
    #  Indicates telephone initiated entry (TEL)
    TEL = "TEL"
    #  Indicates verification only
    EBRONZE = "EBRONZE"
    #  Alias for EBRONZE to match case in tests
    EBronze = EBRONZE


class ReportType(IntEnum):
    """
    Defines the types of reports available in the system.
    Each value is a unique power of 2 to allow for bitwise operations.
    """

    FindTransactions = 1 << 0
    Activity = 1 << 1
    BatchDetail = 1 << 2
    BatchHistory = 1 << 3
    DocumentDisputeDetail = 1 << 3  # Note: Same value as BatchHistory
    BatchSummary = 1 << 4
    OpenAuths = 1 << 5
    Search = 1 << 6
    TransactionDetail = 1 << 7
    FindDeposits = 1 << 8
    DepositDetail = 1 << 11
    DisputeDetail = 1 << 12
    SettlementDisputeDetail = 1 << 13
    FindTransactionsPaged = 1 << 15
    FindSettlementTransactionsPaged = 1 << 16
    FindDepositsPaged = 1 << 17
    FindDisputesPaged = 1 << 18
    FindSettlementDisputesPaged = 1 << 19
    FindStoredPaymentMethodsPaged = 1 << 20
    StoredPaymentMethodDetail = 1 << 21


class AgeIndicator(Enum):
    NoAccount = "NO_ACCOUNT"
    NoChange = "NO_CHANGE"
    ThisTransaction = "THIS_TRANSACTION"
    LessThanThirtyDays = "LESS_THAN_THIRTY_DAYS"
    ThirtyToSixtyDays = "THIRTY_TO_SIXTY_DAYS"
    MoreThanSixtyDays = "MORE_THAN_SIXTY_DAYS"


class CustomerAuthenticationMethod(Enum):
    NotAuthenticated = "NOT_AUTHENTICATED"
    MerchantSystem = "MERCHANT_SYSTEM_AUTHENTICATION"
    FederatedId = "FEDERATED_ID_AUTHENTICATION"
    IssuerCredential = "ISSUER_CREDENTIAL_AUTHENTICATION"
    ThirdParty = "THIRD_PARTY_AUTHENTICATION"
    Fido = "FIDO_AUTHENTICATION"


class DeliveryTimeFrame(Enum):
    ElectronicDelivery = "ELECTRONIC_DELIVERY"
    SameDay = "SAME_DAY"
    Overnight = "OVERNIGHT"
    TwoDaysOrMore = "TWO_DAYS_OR_MORE"


class OrderTransactionType(Enum):
    GoodsServicePurchase = "GOODS_SERVICE_PURCHASE"
    CheckAcceptance = "CHECK_ACCEPTANCE"
    AccountFunding = "ACCOUNT_FUNDING"
    QuasiCashTransaction = "QUASI_CASH_TRANSACTION"
    PrepaidActivationAndLoad = "PREPAID_ACTIVATION_AND_LOAD"


class PhoneNumberType(Enum):
    HOME = "HOME"
    WORK = "WORK"
    SHIPPING = "SHIPPING"
    MOBILE = "MOBILE"


class PreOrderIndicator(Enum):
    MerchandiseAvailable = "MERCHANDISE_AVAILABLE"
    FutureAvailability = "FUTURE_AVAILABILITY"


class PriorAuthenticationMethod(Enum):
    FrictionlessAuthentication = "FRICTIONLESS_AUTHENTICATION"
    ChallengeOccurred = "CHALLENGE_OCCURRED"
    AvsVerified = "AVS_VERIFIED"
    OtherIssuerMethod = "OTHER_ISSUER_METHOD"


class ReorderIndicator(Enum):
    FirstTimeOrder = "FIRST_TIME_ORDER"
    Reorder = "REORDER"


class ShippingMethod(Enum):
    BillingAddress = "BILLING_ADDRESS"
    VerifiedAddress = "ANOTHER_VERIFIED_ADDRESS"
    UnverifiedAddress = "UNVERIFIED_ADDRESS"
    ShipToStore = "SHIP_TO_STORE"
    DigitalGoods = "DIGITAL_GOODS"
    TravelAndEventTickets = "TRAVEL_AND_EVENT_TICKETS"
    Other = "OTHER"


class PaymentMethodName(str, Enum):
    """
    Defines the names of payment methods available in the system.
    """

    APM = "APM"
    DIGITAL_WALLET = "DIGITAL WALLET"
    CARD = "CARD"

    # ACH transaction
    BANK_TRANSFER = "BANK TRANSFER"

    # Open Banking transaction
    BANK_PAYMENT = "BANK PAYMENT"

    # Buy Now Pay Later (BNPL) transaction
    BNPL = "BNPL"


class GatewayProvider(str, Enum):
    """
    Defines the types of gateway providers available in the system.
    """

    GpApi = "GP-API"
    GpEcom = "GP_ECOM"
    Portico = "PORTICO"


class TimeZoneConversion(Enum):
    """
    Indicates how timezones should be handled.
    """

    #  Indicates time is in coordinated universal time (UTC).
    UTC = "UTC"
    #  Indicates the merchant is responsible for timezone conversions.
    Merchant = "Merchant"
    #  Indicates the datacenter, gateway, or processor is responsible for timezone conversions.
    Datacenter = "Datacenter"


class RecurringType(Enum):
    """
    Indicates the type of recurring schedule.
    """

    #  Indicates a fixed number of payments
    Fixed = "Fixed"
    #  Indicates a variable number of payments.
    Variable = "Variable"


class RecurringSequence(Enum):
    """
    Indicates when a transaction is ran in a recurring schedule.
    """

    #  Indicates the transaction is the first of a recurring schedule.
    First = "First"
    #  Indicates the transaction is a subsequent payment of a recurring schedule.
    Subsequent = "Subsequent"
    #  Indicates the transaction is the last of a recurring schedule.
    Last = "Last"


class EmailReceipt(Enum):
    """
    Indicates when an email receipt should be sent for the transaction.
    Currently only used in recurring schedules.
    """

    #  Indicates an email receipt should never be sent.
    Never = "Never"
    #  Indicates an email receipt should always be sent.
    All = "All"
    #  Indicates an email receipt should only be sent on approvals.
    Approvals = "Approvals"
    #  Indicates an email receipt should only be sent on declines.
    Declines = "Declines"


class PaymentSchedule(Enum):
    """
    Indicates when in the month a recurring schedule should run.
    """

    #  Indicates a specified date.
    Dynamic = "Dynamic"
    #  Indicates the first of the month.
    FirstDayOfTheMonth = "FirstDayOfTheMonth"
    #  Indicates the last of the month.
    LastDayOfTheMonth = "LastDayOfTheMonth"


class ScheduleFrequency(Enum):
    """
    Indicates the frequency of a recurring schedule.
    """

    #  Indicates a schedule should process payments weekly.
    Weekly = "Weekly"
    #  Indicates a schedule should process payments bi-weekly (every other week).
    BiWeekly = "Bi-Weekly"
    #  Indicates a schedule should process payments bi-monthly (twice a month).
    BiMonthly = "Bi-Monthly"
    #  Indicates a schedule should process payments semi-monthly (every other month).
    SemiMonthly = "Semi-Monthly"
    #  Indicates a schedule should process payments monthly.
    Monthly = "Monthly"
    #  Indicates a schedule should process payments quarterly.
    Quarterly = "Quarterly"
    #  Indicates a schedule should process payments semi-annually
    SemiAnnually = "Semi-Annually"
    #  Indicates a schedule should process payments annually. (twice a year).
    Annually = "Annually"


class ReasonCode(Enum):
    """
    Indicates a reason for the transaction.
    This is typically used for returns/reversals.
    """

    # Indicates fraud
    Fraud = "FRAUD"
    # Indicates a false positive
    FalsePositive = "FALSEPOSITIVE"
    # Indicates desired good is out of stock
    OutOfStock = "OUTOFSTOCK"
    # Indicates desired good is in stock
    InStock = "INSTOCK"
    # Indicates another reason
    Other = "OTHER"
    # Indicates reason was not given
    NotGiven = "NOTGIVEN"


class HppVersion(Enum):
    """
    Options when specifying HPP versions.
    Useful with `HostedPaymentConfig`.
    """

    #  HPP Version 1
    VERSION_1 = "1"
    #  HPP Version 2
    VERSION_2 = "2"


class FraudFilterMode(Enum):
    """
    Specify how the fraud filter should operate
    """

    #  Fraud filter will behave as configured in RealControl
    NONE = (0,)
    #  Disables the fraud filter
    OFF = (1,)
    #  Sets the fraud filter to passive mode
    PASSIVE = 2


class ReservationProviders(Enum):
    """
    Specifies the reservation service provider
    """

    FreshTxt = 1


class TransactionSortProperty(Enum):
    TIME_CREATED = "TIME_CREATED"
    STATUS = "STATUS"
    TYPE = "TYPE"
    DEPOSIT_ID = "DEPOSIT_ID"
    ID = "ID"


class Secure3dStatus(Enum):
    SUCCESS_AUTHENTICATED = "SUCCESS_AUTHENTICATED"
    SUCCESS_ATTEMPT_MADE = "SUCCESS_ATTEMPT_MADE"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    FAILED = "FAILED"
    NOT_ENROLLED = "NOT_ENROLLED"
    AVAILABLE = "AVAILABLE"
    ENROLLED = "ENROLLED"
    CHALLENGE_REQUIRED = "CHALLENGE_REQUIRED"


class ThreeDSecureVersion(Enum):
    """
    Version of 3ds to use
    """

    One = "One"
    Two = "Two"
    Any = "Any"


class CaptureMode(str, Enum):
    """
    Defines capture modes for transactions.

    AUTO: Capture the transaction automatically
    LATER: Capture the transaction at a later time
    MULTIPLE: Perform multiple captures against the transaction
    """

    AUTO = "AUTO"
    LATER = "LATER"
    MULTIPLE = "MULTIPLE"


class PaymentProvider(Enum):
    OPEN_BANKING = "OPEN_BANKING"


class DisputeStatus(Enum):
    """
    Indicates the status of a dispute.
    """

    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CLOSED = "CLOSED"
    WON = "WON"
    LOST = "LOST"


class DisputeStage(Enum):
    """
    Indicates the stage of a dispute.
    """

    RETRIEVAL = "RETRIEVAL"
    CHARGEBACK = "CHARGEBACK"
    REPRESENTMENT = "REPRESENTMENT"
    SECOND_CHARGEBACK = "SECOND_CHARGEBACK"
    PRE_ARBITRATION = "PRE_ARBITRATION"
    ARBITRATION = "ARBITRATION"


class PaymentMethodUsageMode(Enum):
    """
    Indicates the usage mode of a payment method.
    """

    SINGLE = "SINGLE"
    MULTIPLE = "MULTIPLE"


class EcommerceChannel(Enum):
    """
    Indicates the channel through which the transaction was made.
    """

    ECOM = "ECOM"
    MOTO = "MOTO"
    RETAIL = "RETAIL"


class PayByLinkStatus(Enum):
    """
    Indicates the status of a pay-by-link.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"
    EXPIRED = "EXPIRED"


class IntervalToExpire(Enum):
    """
    Indicates the interval to expire for tokens
    """

    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"


class DccRateType(str, Enum):
    """
    Dynamic Currency Conversion rate types
    """

    Sale = "S"
    Refund = "R"


class DccProcessor(str, Enum):
    """
    Dynamic Currency Conversion processors
    """

    Fexco = "Fexco"
    Euroconex = "Euroconex"


class AuthenticationRequestType(str, Enum):
    PaymentTransaction = "PAYMENT_TRANSACTION"
    RecurringTransaction = "RECURRING_TRANSACTION"
    InstalmentTransaction = "INSTALMENT_TRANSACTION"
    AddCard = "ADD_CARD"
    MaintainCard = "MAINTAIN_CARD"
    CardholderVerification = "CARDHOLDER_VERIFICATION"


class ChallengeRequestIndicator(str, Enum):
    NoPreference = "NO_PREFERENCE"
    NoChallengeRequested = "NO_CHALLENGE_REQUESTED"
    ChallengePreferred = "CHALLENGE_PREFERRED"
    ChallengeMandated = "CHALLENGE_MANDATED"
    NoChallengeRequestedTransactionRiskAnalysisPerformed = (
        "NO_CHALLENGE_REQUESTED_TRANSACTION_RISK_ANALYSIS_PERFORMED"
    )
    NoChallengeRequestedDataShareOnly = "NO_CHALLENGE_REQUESTED_DATA_SHARE_ONLY"
    NoChallengeRequestedScaAlreadyPerformed = (
        "NO_CHALLENGE_REQUESTED_SCA_ALREADY_PERFORMED"
    )
    NoChallengeRequestedWhitelist = "NO_CHALLENGE_REQUESTED_WHITELIST"
    ChallengeRequestedPromptForWhitelist = "CHALLENGE_REQUESTED_PROMPT_FOR_WHITELIST"


class MessageCategory(str, Enum):
    PaymentAuthentication = "PAYMENT_AUTHENTICATION"
    NonPaymentAuthentication = "NON_PAYMENT_AUTHENTICATION"


class MessageVersion(str, Enum):
    Version210 = "2.1.0"


class MethodUrlCompletion(str, Enum):
    Yes = "YES"
    No = "NO"
    Unavailable = "UNAVAILABLE"


from enum import Enum


class SdkInterface(str, Enum):
    Native = "NATIVE"
    Browser = "BROWSER"
    Both = "BOTH"


class DecoupledFlowRequest(Enum):
    DECOUPLED_PREFERRED = "DECOUPLED_PREFERRED"
    DO_NOT_USE_DECOUPLED = "DO_NOT_USE_DECOUPLED"


class SdkUiType(str, Enum):
    Text = "TEXT"
    SingleSelect = "SINGLE_SELECT"
    MultiSelect = "MULTI_SELECT"
    Oob = "OOB"
    HtmlOther = "HTML_OTHER"


class ExemptStatus(Enum):
    LOW_VALUE = "LOW_VALUE"
    TRANSACTION_RISK_ANALYSIS = "TRANSACTION_RISK_ANALYSIS"
    TRUSTED_MERCHANT = "TRUSTED_MERCHANT"
    SECURE_CORPORATE_PAYMENT = "SECURE_CORPORATE_PAYMENT"
    SCA_DELEGATION = "SCA_DELEGATION"


class CardChannel(Enum):
    """
    Represents the channel through which a transaction is processed
    """

    CARD_NOT_PRESENT = "CNP"
    CARD_PRESENT = "CP"


class Environment(Enum):
    Test = "TEST"
    Production = "PRODUCTION"
    Qa = "QA"


class HttpVerb(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


class SearchCriteria(Enum):
    AccountName = "accountName"
    AccountNumberLastFour = "accountNumberLastFour"
    AltPaymentStatus = "altPaymentStatus"
    Amount = "amount"
    AquirerReferenceNumber = "aquirerReferenceNumber"
    AuthCode = "authCode"
    BankRoutingNumber = "bankRoutingNumber"
    BatchId = "batchId"
    BatchSequenceNumber = "batchSequenceNumber"
    BrandReference = "brandReference"
    BuyerEmailAddress = "buyerEmailAddress"
    CardBrand = "cardBrand"
    CardHolderFirstName = "cardHolderFirstName"
    CardHolderLastName = "cardHolderLastName"
    CardHolderPoNumber = "cardHolderPoNumber"
    CardNumberFirstSix = "cardNumberFirstSix"
    CardNumberLastFour = "cardNumberLastFour"
    Channel = "channel"
    CheckFirstName = "checkFirstName"
    CheckLastName = "checkLastName"
    CheckName = "checkName"
    CheckNumber = "checkNumber"
    ClerkId = "clerkId"
    ClientTransactionId = "clientTransactionId"
    Country = "country"
    Currency = "currency"
    CustomerId = "customerId"
    DisputeId = "disputeId"
    DepositReference = ""
    DepositStatus = "depositStatus"
    DisplayName = "displayName"
    EndDate = "endDate"
    FullyCaptured = "fullyCaptured"
    GiftCurrency = "giftCurrency"
    GiftMaskedAlias = "giftMaskedAlias"
    InvoiceNumber = "invoiceNumber"
    IssuerResult = "issuerResult"
    IssuerTransactionId = "issuerTransactionId"
    MerchantId = "merchantId"
    OneTime = "oneTime"
    PaymentEntryMode = "paymentEntryMode"
    PaymentMethodKey = "paymentMethodKey"
    PaymentMethodType = "paymentMethodType"
    PaymentType = "paymentType"
    PaymentMethod = "paymentMethod"
    PaymentMethodName = "paymentMethodName"
    PaymentMethodUsageMode = "paymentMethodUsageMode"
    PaymentProvider = "paymentProvider"
    ReferenceNumber = "referenceNumber"
    SettlementAmount = "settlementAmount"
    ScheduleId = "scheduleId"
    SiteTrace = "siteTrace"
    StartDate = "startDate"
    SystemHierarchy = "systemHierarchy"
    TokenFirstSix = "tokenFirstSix"
    TokenLastFour = "tokenLastFour"
    TransactionStatus = "transactionStatus"
    DisputeStage = "disputeStage"
    DisputeStatus = "disputeStatus"
    DisputeDocumentId = "disputeDocumentId"
    UniqueDeviceId = "uniqueDeviceId"
    UserName = "username"
    Name = "name"
    DepositId = "depositId"
    FromTimeLastUpdated = "fromTimeLastUpdated"
    ToTimeLastUpdated = "toTimeLastUpdated"
    StoredPaymentMethodId = "storedPaymentMethodId"
    StoredPaymentMethodStatus = "storedPaymentMethodStatus"
    ActionType = "actionType"
    ActionId = "actionId"
    Resource = "resource"
    ResourceStatus = "resourceStatus"
    ResourceId = "resourceId"
    MerchantName = "merchantName"
    AppName = "appName"
    Version = "version"
    ResponseCode = "responseCode"
    HttpResponseCode = "httpResponseCode"
    ReturnPii = "returnPii"
    RiskAssessmentMode = "riskAssessmentMode"
    RiskAssessmentResult = "riskAssessmentResult"
    RiskAssessmentReasonCode = "riskAssessmentReasonCode"
    SettlementDisputeId = "settlementDisputeId"
    PayByLinkStatus = "payByLinkStatus"
    Description = "description"
    ExpirationDate = "expirationDate"
    AccountStatus = "accountStatus"
    Address = "address"


class PaymentType(Enum):
    REFUND = "REFUND"
    SALE = "SALE"


class DataServiceCriteria(Enum):
    Amount = "amount"
    BankAccountNumber = "bankAccountNumber"
    CaseId = "caseId"
    CardNumberFirstSix = "cardNumberFirstSix"
    CardNumberLastFour = "cardNumberLastFour"
    CaseNumber = "caseNumber"
    Country = "country"
    Currency = "currency"
    DepositReference = "depositReference"
    EndDepositDate = "endDepositDate"
    EndStageDate = "endStageDate"
    Hierarchy = "hierarchy"
    LocalTransactionEndTime = "localTransactionEndTime"
    LocalTransactionStartTime = "localTransactionStartTime"
    MerchantId = "merchantId"
    OrderId = "orderId"
    StartDepositDate = "startDepositDate"
    StartStageDate = "startStageDate"
    SystemHierarchy = "systemHierarchy"
    Timezone = "timezone"
    StartBatchDate = "startBatchDate"
    EndBatchDate = "endBatchDate"


class Channel(Enum):
    CardNotPresent = "CNP"
    CardPresent = "CP"


class SortDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"


class ExemptionReason(Enum):
    APPLY_EXEMPTION = "APPLY_EXEMPTION"
    EOS_CONTINUE = "CONTINUE"
    FORCE_SECURE = "FORCE_SECURE"
    BLOCK = "BLOCK"


class DateFormat(Enum):
    ISO_8601 = "%Y-%m-%d"  # 2025-06-03
    ISO_8601_WITH_TIME = "%Y-%m-%dT%H:%M:%S"  # 2025-06-03T14:30:25
    ISO_8601_WITH_TIMEZONE = "%Y-%m-%dT%H:%M:%S%z"  # 2025-06-03T14:30:25+0000
    ISO_8601_UTC = "%Y-%m-%dT%H:%M:%SZ"  # 2025-06-03T14:30:25Z
    US_FORMAT = "%m/%d/%Y"  # 06/03/2025
    US_FORMAT_SHORT = "%m/%d/%y"  # 06/03/25
    EUROPEAN_FORMAT = "%d/%m/%Y"  # 03/06/2025
    EUROPEAN_FORMAT_SHORT = "%d/%m/%y"  # 03/06/25
    DASH_FORMAT = "%m-%d-%Y"  # 06-03-2025
    DOT_FORMAT = "%d.%m.%Y"  # 03.06.2025
    MONTH_DAY_YEAR = "%B %d, %Y"  # June 03, 2025
    MONTH_DAY_YEAR_SHORT = "%b %d, %Y"  # Jun 03, 2025
    DAY_MONTH_YEAR = "%d %B %Y"  # 03 June 2025
    DAY_MONTH_YEAR_SHORT = "%d %b %Y"  # 03 Jun 2025
    YEAR_MONTH_DAY = "%Y/%m/%d"  # 2025/06/03
    TIMESTAMP_12H = "%m/%d/%Y %I:%M:%S %p"  # 06/03/2025 02:30:25 PM
    TIMESTAMP_24H = "%m/%d/%Y %H:%M:%S"  # 06/03/2025 14:30:25
    WEEKDAY_MONTH_DAY_YEAR = "%A, %B %d, %Y"  # Tuesday, June 03, 2025
    WEEKDAY_SHORT_FORMAT = "%a, %b %d, %Y"  # Tue, Jun 03, 2025
    COMPACT_FORMAT = "%Y%m%d"  # 20250603
    COMPACT_WITH_TIME = "%Y%m%d%H%M%S"  # 20250603143025
