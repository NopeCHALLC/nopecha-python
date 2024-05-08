import time

import nopecha.error
from nopecha.nopecha_object import NopeCHAObject


class NopeCHARequest(NopeCHAObject):
    @classmethod
    def get_url(cls):
        raise NotImplementedError()

    @classmethod
    def get_retries(cls):
        raise NotImplementedError()

    @classmethod
    def get_interval(cls):
        raise NotImplementedError()

    @classmethod
    def post(cls, **params):
        return cls().request("post", cls.get_url(), params)

    @classmethod
    def get(cls, **params):
        for _ in range(cls.get_retries()):
            time.sleep(cls.get_interval())
            result = cls().request("get", cls.get_url(), params)
            if isinstance(result, nopecha.error.IncompleteJobError):
                continue
            return result
        raise nopecha.error.Timeout('Failed to get results')

    @classmethod
    def solve(cls, **params):
        r = cls.post(**params)
        if isinstance(r, nopecha.error.NopeCHAError):
            raise r
        r = cls.get(id=r['data'])
        if isinstance(r, nopecha.error.NopeCHAError):
            raise r
        return r['data']


class Recognition(NopeCHARequest):
    @classmethod
    def get_url(cls):
        return "/"

    @classmethod
    def get_retries(cls):
        return 120

    @classmethod
    def get_interval(cls):
        return 1


class Token(NopeCHARequest):
    @classmethod
    def get_url(cls):
        return "/token"

    @classmethod
    def get_retries(cls):
        return 180

    @classmethod
    def get_interval(cls):
        return 1


class Balance(NopeCHAObject):
    @classmethod
    def get_url(cls):
        return "/status"

    @classmethod
    def get(cls, **params):
        r = cls().request("get", cls.get_url(), params)
        if isinstance(r, nopecha.error.NopeCHAError):
            raise r
        return r
