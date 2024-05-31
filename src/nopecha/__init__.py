import typing
import warnings


def __getattr__(name: str) -> typing.Any:
    if name in ("Recognition", "Token", "Balance", "api_key"):
        warnings.warn(
            f"the V1 API is deprecated, please migrate to the V2 API",
            DeprecationWarning,
        )
        from . import _v1_compat as compat

        return getattr(compat, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
