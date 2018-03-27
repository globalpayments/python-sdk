class ApiException(Exception):
    """
    a general error occurred
    """

    def __init__(self, message, inner_exception=None):
        Exception.__init__(self, message)
        self.message = message
        self.inner_exception = inner_exception


class BuilderException(ApiException):
    """
    A builder error occurred. Check the method calls against the builder.
    """

    def __init__(self, message=None):
        ApiException.__init__(self, message)


class ConfigurationException(ApiException):
    """
    An account or SDK configuration error occurred.
    """

    def __init__(self, message):
        ApiException.__init__(self, message)


class GatewayException(ApiException):
    """
    An error occurred on the gateway.
    """

    #  the gateway response code
    response_code = None
    #  the gateway response message
    response_message = None

    def __init__(self,
                 message,
                 response_code=None,
                 response_message=None,
                 inner_exception=None):
        ApiException.__init__(self, message, inner_exception)
        self.response_code = response_code
        self.response_message = response_message


class MessageException(ApiException):
    """
    A message to/from the device caused an error.
    """

    def __init__(self, message, inner_exception=None):
        ApiException.__init__(self, message, inner_exception)


class UnsupportedTransactionException(ApiException):
    """
    The built transaction is not supported for the gateway or payment method.
    """

    def __init__(self, message=None):
        ApiException.__init__(
            self, ('Transaction type not supported for this payment method.'
                   if message is None else message))
