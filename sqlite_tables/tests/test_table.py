import unittest

from ..column import (
    IntColumn,
    TextColumn,
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
