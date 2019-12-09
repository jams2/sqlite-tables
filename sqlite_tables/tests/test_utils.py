import unittest
import sqlite3

from ..table import SQLiteTable
from ..column import IntColumn
from ..enums import (
    SQLiteConstraint,
    SQLiteType,
)


CONN = sqlite3.connect(':memory:')


class TestSQLiteTemplate(unittest.TestCase):
    pass


class TestSQLiteConstraint(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(
            'SQLiteConstraint.NOT_NULL',
            repr(SQLiteConstraint.NOT_NULL),
        )


class TestSQLiteType(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(
            'SQLiteType.NUMERIC',
            repr(SQLiteType.NUMERIC),
        )
