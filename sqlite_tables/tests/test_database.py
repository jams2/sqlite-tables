import unittest
import sqlite3
from pathlib import Path

from ..database import (
    SQLiteDatabase,
    db_transaction,
)
from ..exceptions import InvalidDatabaseConfiguration
from ..table import SQLiteTable
from ..column import (
    TextColumn,
    IntListColumn,
)


FIXTURE = Path('./sqlite_tables/tests/test_table.sql')
if not FIXTURE.exists():
    raise ValueError('missing fixture file: test_table.sql')


class TestDBSetup(unittest.TestCase):
    def test_creates_connection(self):
        db = SQLiteDatabase(':memory:')
        self.assertIsInstance(db.connection, sqlite3.Connection)

    def test_invalid_path_and_connection_config(self):
        path = Path('~/test_db.db').expanduser()
        conn = sqlite3.connect(':memory:')
        with self.assertRaises(InvalidDatabaseConfiguration):
            SQLiteDatabase(path=path, connection=conn)

    def test_enumerates_tables(self):
        conn = sqlite3.connect(':memory:')
        with open(FIXTURE) as fd:
            with conn:
                conn.executescript(''.join(line for line in fd))
        db = SQLiteDatabase(connection=conn)
        self.assertEqual(['test_table'], db.existing_tables)


class TestInsert(unittest.TestCase):
    def test_insert_single(self):
        table = SQLiteTable(
            'test_table',
            columns=(
                TextColumn('firstname'),
                TextColumn('lastname'),
            ),
        )
        db = SQLiteDatabase(
            ':memory:',
            tables=(table,)
        )
        db.do_creation()
        db.insert('test_table', {'firstname': 'testuser'})
        match = db.connection.execute(
            "SELECT firstname FROM test_table WHERE firstname = 'testuser'"
        ).fetchone()
        self.assertEqual('testuser', match['firstname'])

    def test_insert_multiple(self):
        table = SQLiteTable(
            'test_table',
            columns=(
                TextColumn('firstname'),
                TextColumn('lastname'),
            ),
        )
        db = SQLiteDatabase(
            ':memory:',
            tables=(table,)
        )
        db.do_creation()
        db.insert('test_table', {'firstname': 'test', 'lastname': 'user'})
        match = db.connection.execute(
            "SELECT * FROM test_table WHERE firstname = 'test'"
        ).fetchone()
        self.assertEqual('test', match['firstname'])
        self.assertEqual('user', match['lastname'])

    def test_insert_int_list(self):
        table = SQLiteTable(
            'test_table',
            columns=(
                TextColumn('firstname'),
                IntListColumn('int_list'),
            ),
        )
        db = SQLiteDatabase(
            ':memory:',
            tables=(table,)
        )
        db.do_creation()
        db.insert('test_table', {'firstname': 'test', 'int_list': [1, 2, 3]})
        match = db.connection.execute(
            "SELECT * FROM test_table WHERE firstname = 'test'"
        ).fetchone()
        self.assertEqual([1, 2, 3], match['int_list'])


class TestTransactionWrapper(unittest.TestCase):
    def get_wrapped_test_func(self):
        @db_transaction
        def wrapped_test_func(x):
            return x
        return wrapped_test_func

    def test_not_receives_connection(self):
        """Must recieve a connection or class instance that
        hasattr(self, 'connection')
        """
        with self.assertRaises(ValueError):
            self.get_wrapped_test_func()(1)

    def test_receives_connection_object(self):
        conn = sqlite3.connect(':memory:')
        self.assertEqual(self.get_wrapped_test_func()(conn), conn)

    def test_handles_class_with_connection(self):
        class TestObject(object):
            def __init__(self):
                self.connection = sqlite3.connect(':memory:')
        self.assertIsInstance(
            self.get_wrapped_test_func()(TestObject()).connection,
            sqlite3.Connection,
        )
