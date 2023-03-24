import os

from nopecha.nopecha import (
    Recognition,
    Token,
    Balance,
)
from nopecha.error import NopeCHAError, InvalidRequestError, IncompleteJobError, RateLimitError, AuthenticationError, InsufficientCreditError, UnknownError, Timeout, APIError, ServiceUnavailableError

api_base = os.environ.get("NOPECHA_API_BASE", "https://api.nopecha.com")
api_key = os.environ.get("NOPECHA_API_KEY")
proxy = None

__all__ = [
    "Recognition",
    "Token",
    "Balance",

    "NopeCHAError",
    "InvalidRequestError",
    "IncompleteJobError",
    "RateLimitError",
    "AuthenticationError",
    "InsufficientCreditError",
    "UnknownError",
    "Timeout",
    "APIError",
    "ServiceUnavailableError",

    "api_base",
    "api_key",
    "proxy",
]
