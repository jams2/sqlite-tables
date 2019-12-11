from enum import Enum


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
    BOOL = 'BOOL'

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)


class SQLiteConstant(str, Enum):
    CURRENT_TIMESTAMP = 'CURRENT_TIMESTAMP'
    CURRENT_TIME = 'CURRENT_TIME'
    CURRENT_DATE = 'CURRENT_DATE'

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)
