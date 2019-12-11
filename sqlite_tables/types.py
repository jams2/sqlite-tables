def adapt_bool(boolean: bool) -> bytes:
    """ Python bool type to bytes.
    """
    return str(int(boolean)).encode('ascii')


def convert_bool(i: bytes) -> bool:
    """ SQLite bytes to bool
    """
    return bool(int(i))
