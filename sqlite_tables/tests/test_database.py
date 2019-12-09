import unittest
import os
import sqlite3
from pathlib import Path

from ..database import SQLiteDatabase


FIXTURE = Path('./sqlite_tables/tests/test_table.sql')
if not FIXTURE.exists():
    raise ValueError('missing fixture file: test_table.sql')


class TestDBSetup(unittest.TestCase):
    def test_creates_connection(self):
        db = SQLiteDatabase(':memory:')
        self.assertIsInstance(db.connection, sqlite3.Connection)

    def test_enumerates_tables(self):
        conn = sqlite3.connect(':memory:')
        with open(FIXTURE) as fd:
            with conn:
                conn.executescript(''.join(line for line in fd))
        db = SQLiteDatabase('', connection=conn)
        self.assertEqual(['test_table'], db.tables)
