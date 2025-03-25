from globalpayments.api.entities.enums import ThreeDSecureVersion


class ThreeDSecure(object):
    enrolled = None
    payer_authentication_response = None
    issuer_acs_url = None

    status = None
    eci = None
    xid = None
    cavv = None
    version = ThreeDSecureVersion.Any
    algorithm = None
