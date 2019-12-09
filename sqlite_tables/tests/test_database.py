import unittest
import os
import sqlite3
from pathlib import Path

from ..database import SQLiteDatabase
from ..exceptions import InvalidDatabaseConfiguration


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

    def test_insert_single(self):
        conn = sqlite3.connect(':memory:')
        with open(FIXTURE) as fd:
            with conn:
                conn.executescript(''.join(line for line in fd))
        db = SQLiteDatabase(connection=conn)
        db.insert('test_table', {'firstname': 'testuser'})
        match = db.connection.execute(
            "SELECT firstname FROM test_table WHERE firstname = 'testuser'"
        ).fetchone()
        self.assertEqual('testuser', match['firstname'])

    def test_insert_multiple(self):
        conn = sqlite3.connect(':memory:')
        with open(FIXTURE) as fd:
            with conn:
                conn.executescript(''.join(line for line in fd))
        db = SQLiteDatabase(connection=conn)
        db.insert('test_table', {'firstname': 'test', 'lastname': 'user'})
        match = db.connection.execute(
            "SELECT * FROM test_table WHERE firstname = 'test'"
        ).fetchone()
        self.assertEqual('test', match['firstname'])
        self.assertEqual('user', match['lastname'])
