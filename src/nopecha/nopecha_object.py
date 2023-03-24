import json
from copy import deepcopy

from nopecha import api_requestor


class NopeCHAObject(dict):
    api_base_override = None

    def __init__(self, api_key=None, api_base=None, **params):
        super(NopeCHAObject, self).__init__()

        self._retrieve_params = params
        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(self, "api_base_override", api_base)

    def __setattr__(self, k, v):
        if k[0] == "_" or k in self.__dict__:
            return super(NopeCHAObject, self).__setattr__(k, v)
        self[k] = v
        return None

    def __getattr__(self, k):
        if k[0] == "_":
            raise AttributeError(k)
        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __delattr__(self, k):
        if k[0] == "_" or k in self.__dict__:
            return super(NopeCHAObject, self).__delattr__(k)
        else:
            del self[k]

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(f"You cannot set {k} to an empty string. We interpret empty strings as None in requests. You may set {str(self)}.{k} = None to delete the property")
        super(NopeCHAObject, self).__setitem__(k, v)

    def __delitem__(self, k):
        raise NotImplementedError("del is not supported")

    def __setstate__(self, state):
        self.update(state)

    def __reduce__(self):
        return (type(self), (self.api_key,), dict(self))

    @classmethod
    def api_base(cls):
        return None

    def request(self, method, url, params=None, headers=None, request_timeout=None):
        if params is None:
            params = self._retrieve_params
        requestor = api_requestor.APIRequestor(key=self.api_key, api_base=self.api_base_override or self.api_base())
        return requestor.request(method, url, params=params, headers=headers, request_timeout=request_timeout)

    def __repr__(self):
        ident_parts = [type(self).__name__]
        obj = self.get("object")
        if isinstance(obj, str):
            ident_parts.append(obj)
        return "<%s at %s> JSON: %s" % (
            " ".join(ident_parts),
            hex(id(self)),
            str(self),
        )

    def __str__(self):
        obj = self.to_dict_recursive()
        return json.dumps(obj, sort_keys=True, indent=2)

    def to_dict(self):
        return dict(self)

    def to_dict_recursive(self):
        d = dict(self)
        for k, v in d.items():
            if isinstance(v, NopeCHAObject):
                d[k] = v.to_dict_recursive()
            elif isinstance(v, list):
                d[k] = [e.to_dict_recursive() if isinstance(e, NopeCHAObject) else e for e in v]
        return d

    def __copy__(self):
        copied = NopeCHAObject(self.api_key)
        copied._retrieve_params = self._retrieve_params
        for k, v in self.items():
            super(NopeCHAObject, copied).__setitem__(k, v)
        return copied

    def __deepcopy__(self, memo):
        copied = self.__copy__()
        memo[id(self)] = copied
        for k, v in self.items():
            super(NopeCHAObject, copied).__setitem__(k, deepcopy(v, memo))
        return copied
