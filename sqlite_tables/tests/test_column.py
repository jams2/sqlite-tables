import unittest

from ..column import (
    IntColumn,
    RealColumn,
    NumericColumn,
    TextColumn,
)
from ..exceptions import InvalidColumnConfiguration
from ..utils import SQLiteType


class TestColumnDefToSQL(unittest.TestCase):
    def test_sqlite_type(self):
        col = IntColumn('test_col')
        self.assertEqual(SQLiteType.INT, col.sqlite_type)

    def test_not_null_to_sql(self):
        col = IntColumn('test_col', allow_null=False)
        self.assertEqual('test_col INT NOT NULL', col.definition_to_sql())

    def test_default(self):
        col = IntColumn('test_col', allow_null=False, default=0)
        self.assertEqual('test_col INT NOT NULL DEFAULT 0', col.definition_to_sql())

    def test_unique(self):
        col = IntColumn('test_col', allow_null=False, unique=True)
        self.assertEqual('test_col INT NOT NULL UNIQUE', col.definition_to_sql())

    def test_is_primary_key(self):
        col = IntColumn('test_col', is_primary_key=True)
        self.assertEqual('test_col INT PRIMARY KEY', col.definition_to_sql())

    def test_is_primary_key_not_null(self):
        col = IntColumn('test_col', is_primary_key=True, allow_null=False)
        self.assertEqual('test_col INT NOT NULL PRIMARY KEY', col.definition_to_sql())

    def test_real_column_type_correct(self):
        col = RealColumn('test_col', unique=True)
        self.assertEqual('test_col REAL UNIQUE', col.definition_to_sql())

    def test_text_column_type_correct(self):
        col = TextColumn('test_col')
        self.assertEqual('test_col TEXT', col.definition_to_sql())

    def test_text_column_wraps_default_value(self):
        """A string should be wrapped in quote marks.
        """
        col = TextColumn('test_col', default='test string')
        self.assertEqual('test_col TEXT DEFAULT "test string"', col.definition_to_sql())

    def test_numeric_column_type_correct(self):
        col = NumericColumn('test_col')
        self.assertEqual('test_col NUMERIC', col.definition_to_sql())

    def test_numeric_column_default(self):
        col = NumericColumn('test_col', default=1.2)
        self.assertEqual('test_col NUMERIC DEFAULT 1.2', col.definition_to_sql())

    def test_raises_unique_and_primary_key(self):
        with self.assertRaises(InvalidColumnConfiguration):
            IntColumn('test_col', is_primary_key=True, unique=True).definition_to_sql()

    def test_primary_key_with_default(self):
        with self.assertRaises(InvalidColumnConfiguration):
            IntColumn('test_col', is_primary_key=True, default=2).definition_to_sql()

    def test_repr(self):
        col = TextColumn('test_col', unique=True, allow_null=False)
        self.assertEqual(
            f"TextColumn('test_col', SQLiteType.TEXT, allow_null=False, default=None, "
            f"is_foreign_key=False, fk_column_ref=None, fk_table_ref=None, "
            f"is_primary_key=False, unique=True)",
            repr(col),
        )

    def test_str(self):
        col = TextColumn('test_col', unique=True, allow_null=False)
        self.assertEqual(
            "<TextColumn: 'test_col'>",
            str(col),
        )


class TestForeignKeyConstraintToSQL(unittest.TestCase):
    def test_fk_constraint_to_sql(self):
        col = IntColumn(
            'fk_id',
            is_foreign_key=True,
            fk_table_ref='other_table',
            fk_column_ref='other_col',
        )
        self.assertEqual(
            'FOREIGN KEY (fk_id) REFERENCES other_table (other_col)',
            col.fk_constraint_to_sql(),
        )

    def test_no_table_ref_throws(self):
        with self.assertRaises(InvalidColumnConfiguration):
            IntColumn(
                'fk_id',
                is_foreign_key=True,
                fk_column_ref='other_col',
            ).fk_constraint_to_sql()

    def test_no_col_ref_throws(self):
        with self.assertRaises(InvalidColumnConfiguration):
            IntColumn(
                'fk_id',
                is_foreign_key=True,
                fk_table_ref='other_col',
            ).fk_constraint_to_sql()
