import typing
from logging import getLogger

try:
    import requests
except ImportError:
    raise ImportError("You must install 'requests' to use `nopecha.api.requests`")

from ._base import APIClient, UniformResponse

logger = getLogger(__name__)
__all__ = ["RequestsAPIClient"]


class RequestsAPIClient(APIClient):
    session: requests.Session

    def __init__(self, *args, **kwargs):
        session = kwargs.pop("session", None)
        super().__init__(*args, **kwargs)

        if session is None:
            session = requests.Session()
        self.session = session

    def _request_raw(
        self, method: str, url: str, body: typing.Optional[dict] = None
    ) -> UniformResponse:
        status = 999
        try:
            response = self.session.request(
                method, url, json=body, headers=self._get_headers()
            )
            status = response.status_code
            return UniformResponse(status, response.json())
        except Exception as e:
            logger.warning("Request failed: %s", e)
            return UniformResponse(status, None)
