try:
    from requests import get
except ImportError:
    from urllib.request import Request, urlopen
    from http.client import HTTPResponse

    def request(url: str) -> bytes:
        request = Request(url)
        response = urlopen(request)
        assert isinstance(response, HTTPResponse)
        return response.read()

else:

    def request(url: str) -> bytes:
        return get(url).content


__all__ = ["request"]
