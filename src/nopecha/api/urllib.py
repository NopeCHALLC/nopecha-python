import typing
from json import dumps, loads
from logging import getLogger
from urllib.request import urlopen, Request
from http.client import HTTPResponse

from ._base import APIClient, UniformResponse

logger = getLogger(__name__)
__all__ = ["UrllibAPIClient"]


class UrllibAPIClient(APIClient):
    def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        status = 999
        try:
            request = Request(
                url,
                dumps(body).encode("utf-8") if body is not None else None,
                headers=self._get_headers(),
                method=method,
            )
            response = urlopen(request)
            assert isinstance(response, HTTPResponse)
            status = response.status
            response_body = response.read()
            return UniformResponse(status, loads(response_body))
        except Exception as e:
            logger.warning("Request failed: %s", e)
            return UniformResponse(status, None)
