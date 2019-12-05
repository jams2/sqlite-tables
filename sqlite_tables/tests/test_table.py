import unittest

from ..column import (
    IntColumn,
    TextColumn,
    DateTimeColumn,
    TimeColumn,
    DateColumn,
)
from ..exceptions import InvalidTableConfiguration
from ..table import DatabaseTable


class TestTableToSQL(unittest.TestCase):
    def test_no_column_names_raises(self):
        with self.assertRaises(InvalidTableConfiguration):
            DatabaseTable('test_table').schema_to_sql()

    def test_duplicate_columns_raises(self):
        with self.assertRaises(InvalidTableConfiguration):
            DatabaseTable(
                'test_table',
                columns=(IntColumn('new_column'), TextColumn('new_column')),
            ).schema_to_sql()

    def test_unique_together(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                TextColumn('firstname'),
                TextColumn('lastname'),
            ),
            unique_together=('firstname', 'lastname'),
        )
        self.assertEqual(
            f'CREATE TABLE IF NOT EXISTS test_table '
            f'(firstname TEXT, lastname TEXT, UNIQUE (firstname, lastname))',
            table.schema_to_sql()
        )

    def test_no_id_column(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                TextColumn('firstname'),
                TextColumn('lastname'),
            ),
        )
        self.assertEqual(
            'CREATE TABLE IF NOT EXISTS test_table (firstname TEXT, lastname TEXT)',
            table.schema_to_sql()
        )

    def test_specified_id_column(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                IntColumn('id', is_primary_key=True),
                TextColumn('firstname'),
                TextColumn('lastname'),
            ),
        )
        self.assertEqual(
            f'CREATE TABLE IF NOT EXISTS test_table '
            f'(id INT PRIMARY KEY, firstname TEXT, lastname TEXT)',
            table.schema_to_sql()
        )

    def test_unique_together_and_id(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                IntColumn('id', is_primary_key=True),
                TextColumn('firstname'),
                TextColumn('lastname'),
            ),
            unique_together=('firstname', 'lastname'),
        )
        self.assertEqual(
            f'CREATE TABLE IF NOT EXISTS test_table '
            f'(id INT PRIMARY KEY, firstname TEXT, lastname TEXT, '
            f'UNIQUE (firstname, lastname))',
            table.schema_to_sql()
        )

    def test_foreign_key_constraint(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                IntColumn('id', is_primary_key=True),
                IntColumn(
                    'fk_col',
                    is_foreign_key=True,
                    fk_table_ref='other_table',
                    fk_column_ref='id',
                )
            ),
        )
        self.assertEqual(
            f'CREATE TABLE IF NOT EXISTS test_table '
            f'(id INT PRIMARY KEY, fk_col INT, '
            f'FOREIGN KEY (fk_col) REFERENCES other_table (id))',
            table.schema_to_sql()
        )

    def test_foreign_key_and_unique_together(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                IntColumn('id', is_primary_key=True),
                IntColumn(
                    'fk_col',
                    is_foreign_key=True,
                    fk_table_ref='other_table',
                    fk_column_ref='id',
                )
            ),
            unique_together=('firstname', 'lastname'),
        )
        self.assertEqual(
            f'CREATE TABLE IF NOT EXISTS test_table '
            f'(id INT PRIMARY KEY, fk_col INT, '
            f'FOREIGN KEY (fk_col) REFERENCES other_table (id), '
            f'UNIQUE (firstname, lastname))',
            table.schema_to_sql()
        )

    def test_multiple_unique_constraints(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                IntColumn('id', is_primary_key=True),
                TextColumn('firstname'),
                TextColumn('nickname'),
                TextColumn('lastname'),
            ),
            unique_together=(
                ('firstname', 'lastname'),
                ('firstname', 'nickname'),
            ),
        )
        self.assertEqual(
            f'CREATE TABLE IF NOT EXISTS test_table '
            f'(id INT PRIMARY KEY, firstname TEXT, nickname TEXT, lastname TEXT, '
            f'UNIQUE (firstname, lastname), '
            f'UNIQUE (firstname, nickname))',
            table.schema_to_sql()
        )

    def test_repr(self):
        table = DatabaseTable(
            'test_table',
            columns=(IntColumn('id', is_primary_key=True),),
        )
        self.assertEqual(
            f"DatabaseTable('test_table', columns=(IntColumn('id', SQLiteType.INT, "
            f"allow_null=True, default=None, is_foreign_key=False, fk_column_ref=None, "
            f"fk_table_ref=None, is_primary_key=True, unique=False),), "
            f"unique_together=(), raise_exists_error=False)",
            repr(table),
        )

    def test_str(self):
        table = DatabaseTable(
            'test_table',
            columns=(IntColumn('id', is_primary_key=True),),
        )
        self.assertEqual(
            "<DatabaseTable: 'test_table'>",
            str(table),
        )


class TestTriggersToSQL(unittest.TestCase):
    def test_datetime_auto_update(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                DateTimeColumn('datetime', auto_now_insert=True, auto_now_update=True),
            ),
        )
        self.assertEqual(
            f'CREATE TRIGGER test_table_datetime_update AFTER UPDATE ON test_table '
            f'BEGIN UPDATE test_table SET datetime = CURRENT_TIMESTAMP WHERE '
            f'rowid = old.rowid; END',
            table.triggers_to_sql()[0],
        )

    def test_date_auto_update(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                DateColumn('date', auto_now_insert=True, auto_now_update=True),
            ),
        )
        self.assertEqual(
            f'CREATE TRIGGER test_table_date_update AFTER UPDATE ON test_table '
            f'BEGIN UPDATE test_table SET date = CURRENT_DATE WHERE '
            f'rowid = old.rowid; END',
            table.triggers_to_sql()[0],
        )

    def test_time_auto_update(self):
        table = DatabaseTable(
            'test_table',
            columns=(
                TimeColumn('time', auto_now_insert=True, auto_now_update=True),
            ),
        )
        self.assertEqual(
            f'CREATE TRIGGER test_table_time_update AFTER UPDATE ON test_table '
            f'BEGIN UPDATE test_table SET time = CURRENT_TIME WHERE '
            f'rowid = old.rowid; END',
            table.triggers_to_sql()[0],
        )
