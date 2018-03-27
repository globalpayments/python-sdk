from globalpayments.api.entities import EncryptionData
from globalpayments.api.entities.enums import EntryMethod, TaxType, TransactionModifier
from globalpayments.api.payment_methods import CreditCardData, CreditTrackData, DebitTrackData, EBTCardData, EBTTrackData, GiftCard


class TestCards(object):
    @staticmethod
    def as_debit(card, pin_block):
        data = DebitTrackData()
        data.value = card.value
        data.encryption_data = card.encryption_data
        data.pin_block = pin_block
        return data

    @staticmethod
    def as_ebt(card, pin_block):
        data = None
        if isinstance(card, CreditTrackData):
            data = EBTTrackData()
            data.value = card.value
            data.encryption_data = card.encryption_data
        if isinstance(card, CreditCardData):
            data = EBTCardData()
            data.number = card.number
            data.exp_month = card.exp_month
            data.exp_year = card.exp_year
            data.reader_present = card.reader_present
            data.card_present = card.card_present
        data.pin_block = pin_block
        return data

    @staticmethod
    def visa_manual(card_present=False, reader_present=False):
        data = CreditCardData()
        data.number = '4012002000060016'
        data.exp_month = '12'
        data.exp_year = '2025'
        data.cvn = '123'
        data.card_present = card_present
        data.reader_present = reader_present
        return data

    @staticmethod
    def visa_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B4012002000060016^VI TEST CREDIT^251210118039000000000396?;4012002000060016=25121011803939600000?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def visa_swipe_encrypted(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '<E1050711%B4012001000000016^VI TEST CREDIT^251200000000000000000000?|LO04K0WFOmdkDz0um+GwUkILL8ZZOP6Zc4rCpZ9+kg2T3JBT4AEOilWTI|+++++++Dbbn04ekG|11;4012001000000016=25120000000000000000?|1u2F/aEhbdoPixyAPGyIDv3gBfF|+++++++Dbbn04ekG|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>;'
        data.entry_method = entry_method
        data.encryption_data = EncryptionData()
        data.encryption_data.version = '01'
        return data

    @staticmethod
    def mastercard_manual(card_present=False, reader_present=False):
        data = CreditCardData()
        data.number = '5473500000000014'
        data.exp_month = '12'
        data.exp_year = '2025'
        data.cvn = '123'
        data.card_present = card_present
        data.reader_present = reader_present
        return data

    @staticmethod
    def mastercard_series2_manual(card_present=False, reader_present=False):
        data = CreditCardData()
        data.number = '2223000010005798'
        data.exp_month = '12'
        data.exp_year = '2019'
        data.cvn = '999'
        data.card_present = card_present
        data.reader_present = reader_present
        return data

    @staticmethod
    def mastercard_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B5473500000000014^MC TEST CARD^251210199998888777766665555444433332?;5473500000000014=25121019999888877776?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def mastercard_24_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B2223000010005780^TEST CARD/EMV BIN-2^19121010000000009210?;2223000010005780=19121010000000009210?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def mastercard_25_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B2223000010005798^TEST CARD/EMV BIN-2^19121010000000003840?;2223000010005798=19121010000000003840?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def mastercard_swipe_encrypted(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '<E1052711%B5473501000000014^MC TEST CARD^251200000000000000000000000000000000?|GVEY/MKaKXuqqjKRRueIdCHPPoj1gMccgNOtHC41ymz7bIvyJJVdD3LW8BbwvwoenI+|+++++++C4cI2zjMp|11;5473501000000014=25120000000000000000?|8XqYkQGMdGeiIsgM0pzdCbEGUDP|+++++++C4cI2zjMp|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>'
        data.entry_method = entry_method
        data.encryption_data = EncryptionData()
        data.encryption_data.version = '01'
        return data

    @staticmethod
    def discover_manual(card_present=False, reader_present=False):
        data = CreditCardData()
        data.number = '6011000990156527'
        data.exp_month = '12'
        data.exp_year = '2025'
        data.cvn = '123'
        data.card_present = card_present
        data.reader_present = reader_present
        return data

    @staticmethod
    def discover_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B6011000990156527^DIS TEST CARD^25121011000062111401?;6011000990156527=25121011000062111401?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def discover_swipe_encrypted(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '<E1049711%B6011000000006527^DIS TEST CARD^25120000000000000000?|nqtDvLuS4VHJd1FymxBxihO5g/ZDqlHyTf8fQpjBwkk95cc6PG9V|+++++++C+LdWXLpP|11;6011000000006527=25120000000000000000?|8VfZvczP6iBqRis2XFypmktaipa|+++++++C+LdWXLpP|00|||/wECAQECAoFGAgEH2wYcShV78RZwb3NAc2VjdXJlZXhjaGFuZ2UubmV0PX50qfj4dt0lu9oFBESQQNkpoxEVpCW3ZKmoIV3T93zphPS3XKP4+DiVlM8VIOOmAuRrpzxNi0TN/DWXWSjUC8m/PI2dACGdl/hVJ/imfqIs68wYDnp8j0ZfgvM26MlnDbTVRrSx68Nzj2QAgpBCHcaBb/FZm9T7pfMr2Mlh2YcAt6gGG1i2bJgiEJn8IiSDX5M2ybzqRT86PCbKle/XCTwFFe1X|>'
        data.entry_method = entry_method
        data.encryption_data = EncryptionData()
        data.encryption_data.version = '01'
        return data

    @staticmethod
    def amex_manual(card_present=False, reader_present=False):
        data = CreditCardData()
        data.number = '372700699251018'
        data.exp_month = '12'
        data.exp_year = '2025'
        data.cvn = '1234'
        data.card_present = card_present
        data.reader_present = reader_present
        return data

    @staticmethod
    def amex_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B3727 006992 51018^AMEX TEST CARD^2512990502700?;372700699251018=2512990502700?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def jcb_manual(card_present=False, reader_present=False):
        data = CreditCardData()
        data.number = '3566007770007321'
        data.exp_month = '12'
        data.exp_year = '2025'
        data.cvn = '123'
        data.card_present = card_present
        data.reader_present = reader_present
        return data

    @staticmethod
    def jcb_swipe(entry_method=EntryMethod.Swipe):
        data = CreditTrackData()
        data.value = '%B3566007770007321^JCB TEST CARD^2512101100000000000000000064300000?;3566007770007321=25121011000000076435?'
        data.entry_method = entry_method
        return data

    @staticmethod
    def gsb_manual():
        data = CreditCardData()
        data.number = '6277220572999800'
        data.exp_month = '12'
        data.exp_year = '2049'
        return data

    @staticmethod
    def gift_card_1_swipe():
        data = GiftCard()
        data.track_data = '%B5022440000000000098^^391200081613?;5022440000000000098=391200081613?'
        return data

    @staticmethod
    def gift_card_2_manual():
        data = GiftCard()
        data.number = '5022440000000000007'
        return data
