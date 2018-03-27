class EncryptionData(object):
    """
    Details how encrypted track data was encrypted by the device
    in order for the gateway to decrypt the data.
    """

    version = None
    track_number = None
    ksn = None
    ktb = None

    @staticmethod
    def version_1():
        rvalue = EncryptionData()
        rvalue.version = '01'
        return rvalue

    @staticmethod
    def version_2(ktb, track_number=None):
        rvalue = EncryptionData()
        rvalue.version = '02'
        rvalue.ktb = ktb
        rvalue.track_number = track_number
        return rvalue
