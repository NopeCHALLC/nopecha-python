import typing
from logging import getLogger

from aiohttp import ClientSession

try:
    import aiohttp
except ImportError:
    raise ImportError("You must install 'aiohttp' to use `nopecha.api.aiohttp`")

from ._base import AsyncAPIClient, UniformResponse

logger = getLogger(__name__)
__all__ = ["AsyncHTTPXAPIClient"]


class AsyncHTTPXAPIClient(AsyncAPIClient):
    client: aiohttp.ClientSession

    def __init__(self, *args, client: ClientSession, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = client

    async def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        status = 999
        try:
            async with self.client.request(
                method, url, json=body, headers=self._get_headers()
            ) as response:
                status = response.status
                return UniformResponse(status, await response.json())
        except Exception as e:
            logger.warning("Request failed: %s", e)
            return UniformResponse(status, None)
