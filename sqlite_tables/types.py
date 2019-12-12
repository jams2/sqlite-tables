from typing import (
    Iterable,
    Generator,
)


def adapt_bool(boolean: bool) -> bytes:
    return str(int(boolean)).encode('ascii')


def convert_bool(i: bytes) -> bool:
    return bool(int(i))


class IntList(list):
    pass


def adapt_int_list(int_list: IntList) -> bytes:
    if len(int_list) == 0:
        return b''
    return ','.join(str(i) for i in int_list).encode('ascii')


def convert_int_list(comma_separated_ints: bytes) -> IntList:
    if len(comma_separated_ints) == 0 or comma_separated_ints is None:
        return IntList([])
    return IntList(int(i) for i in comma_separated_ints.decode().split(','))
