import unittest
import sqlite3

from ..table import SQLiteTable
from ..column import IntColumn
from ..utils import (
    has_table,
    SQLiteConstraint,
    SQLiteType,
    SQLiteTemplate,
)


CONN = sqlite3.connect(':memory:')


class TestHasTable(unittest.TestCase):
    def test_has_table(self):
        test_table = SQLiteTable(
            'test_table',
            columns=(IntColumn('id', is_primary_key=True, allow_null=False),),
        )
        with CONN:
            CONN.execute(test_table.schema_to_sql())
        self.assertTrue(has_table(CONN, 'test_table'))

    def test_not_has_table(self):
        CONN.execute('DROP TABLE IF EXISTS test_table')
        self.assertFalse(has_table(CONN, 'test_table'))


class TestTransactionDecorator(unittest.TestCase):
    def test_raises_value_error(self):
        with self.assertRaises(ValueError):
            has_table({}, 'test_table')


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
