import unittest

from ..enums import (
    SQLiteConstraint,
    SQLiteType,
)


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
