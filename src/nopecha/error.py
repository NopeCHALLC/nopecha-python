class NopeCHAError(Exception):
    def __init__(self, message=None, http_body=None, http_status=None, json_body=None, headers=None):
        super(NopeCHAError, self).__init__(message)

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body
        self.headers = headers or {}

    def __str__(self):
        return f"{type(self).__name__}: {self._message}" or "<empty message>"


class InvalidRequestError(NopeCHAError):
    pass


class IncompleteJobError(NopeCHAError):
    pass


class RateLimitError(NopeCHAError):
    pass


class AuthenticationError(NopeCHAError):
    pass


class InsufficientCreditError(NopeCHAError):
    pass


class UnknownError(NopeCHAError):
    pass


class Timeout(NopeCHAError):
    pass


class APIError(NopeCHAError):
    pass


class ServiceUnavailableError(NopeCHAError):
    pass
