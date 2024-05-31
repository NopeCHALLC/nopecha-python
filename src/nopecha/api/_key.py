from re import compile

_free_key_format = compile(r"[a-z\d]{16}")


def is_free_key(key: str) -> bool:
    return bool(_free_key_format.fullmatch(key))
