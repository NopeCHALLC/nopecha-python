# Compatibility layer for v1 API
import os
import typing

from nopecha.api.types import RecognitionRequest, TokenRequest

# urllib is available everywhere, so we can always use this
from .api.urllib import UrllibAPIClient


api_key = os.getenv("NOPECHA_API_KEY", "")
client = UrllibAPIClient(api_key)


class Token:
    @classmethod
    def solve(cls, **kwargs):
        client.key = api_key
        return client.solve_raw(typing.cast(TokenRequest, kwargs))


class Recognition:
    @classmethod
    def solve(cls, **kwargs):
        client.key = api_key
        return client.recognize_raw(typing.cast(RecognitionRequest, kwargs))


class Balance:
    @classmethod
    def get(cls):
        client.key = api_key
        return client.status()
