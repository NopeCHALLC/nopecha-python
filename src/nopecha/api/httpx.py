import typing
from logging import getLogger

try:
    import httpx
except ImportError:
    raise ImportError("You must install 'httpx' to use `nopecha.api.httpx`")

from ._base import APIClient, AsyncAPIClient, UniformResponse

logger = getLogger(__name__)
__all__ = ["HTTPXAPIClient", "AsyncHTTPXAPIClient"]


class HTTPXAPIClient(APIClient):
    client: httpx.Client

    def __init__(self, *args, **kwargs):
        client = kwargs.pop("client", None)
        super().__init__(*args, **kwargs)

        if client is None:
            client = httpx.Client()
        elif isinstance(client, httpx.AsyncClient):
            raise TypeError(
                "Expected httpx.Client, got httpx.AsyncClient. Use `nopecha.api.httpx.AsyncHTTPXAPIClient` for async usage instead."
            )
        self.client = client

    def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        status = 999
        try:
            response = self.client.request(
                method, url, json=body, headers=self._get_headers()
            )
            status = response.status_code
            return UniformResponse(status, response.json())
        except Exception as e:
            logger.warning("Request failed: %s", e)
            return UniformResponse(status, None)


class AsyncHTTPXAPIClient(AsyncAPIClient):
    client: httpx.AsyncClient

    def __init__(self, *args, **kwargs):
        client = kwargs.pop("client", None)
        super().__init__(*args, **kwargs)

        if client is None:
            client = httpx.AsyncClient()
        elif isinstance(client, httpx.Client):
            raise TypeError(
                "Expected httpx.AsyncClient, got httpx.Client. Use `nopecha.api.httpx.HTTPXAPIClient` for sync usage instead."
            )
        self.client = client

    async def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        status = 999
        try:
            response = await self.client.request(
                method, url, json=body, headers=self._get_headers()
            )
            status = response.status_code
            return UniformResponse(status, response.json())
        except Exception as e:
            logger.warning("Request failed: %s", e)
            return UniformResponse(status, None)
