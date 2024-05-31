import typing
from json import dumps, loads
from logging import getLogger
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
# from http.client import HTTPResponse

from ._base import APIClient, UniformResponse

logger = getLogger(__name__)
__all__ = ["UrllibAPIClient"]


class UrllibAPIClient(APIClient):
    def _get_headers(self) -> dict:
        headers = super()._get_headers()
        headers.update({ "content-type": "application/json" })
        return headers

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

            try:
                response = urlopen(request)
            except HTTPError as e:
                response = e  # Here, e is an HTTPError object that acts like a response object

            status = response.status
            response_body = response.read().decode("utf-8")  # Decode to string

            return UniformResponse(status, loads(response_body) if response_body else None)

        except URLError as e:
            # Handle URL errors that occur from unreachable URLs or network issues
            logger.warning("URL Error: %s", e)
            return UniformResponse(status, None)

        except Exception as e:
            logger.warning("Request failed: %s", e)
            return UniformResponse(status, None)
