import re
import sqlite3
from enum import Enum
from string import Template

from .database import (
    SQLiteDatabase,
    db_transaction,
)


@db_transaction
def has_table(conn: sqlite3.Connection, table_name: str) -> bool:
    cursor = conn.execute(
        'SELECT count(*) FROM sqlite_master WHERE type="table" AND name=?',
        (table_name,),
    )
    result = cursor.fetchone()
    return result is not None and result[0] > 0


class SQLiteConstraint(str, Enum):
    NOT_NULL = 'NOT NULL'
    UNIQUE = 'UNIQUE'
    DEFAULT = 'DEFAULT'
    PRIMARY_KEY = 'PRIMARY KEY'
    IF_NOT_EXISTS = 'IF NOT EXISTS'

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)


class SQLiteType(str, Enum):
    INT = 'INT'
    TEXT = 'TEXT'
    REAL = 'REAL'
    NUMERIC = 'NUMERIC'
    BLOB = 'BLOB'

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)


class SQLiteConstant(str, Enum):
    CURRENT_TIMESTAMP = 'CURRENT_TIMESTAMP'
    CURRENT_TIME = 'CURRENT_TIME'
    CURRENT_DATE = 'CURRENT_DATE'

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)


class SQLiteTemplate(Template):
    '''Overrides the substitute method to replace multiple occurences
    of whitespace with one.
    '''
    ws_pattern = re.compile(r'(?<=\s)\s+|\s+$|\s+(?=\)$)|(?<=\s)\s+(?=\))')

    def substitute(self, *args, **kwargs):
        return self.ws_pattern.sub('', super().substitute(*args, **kwargs))
