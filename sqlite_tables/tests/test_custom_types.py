import unittest
import sqlite3

from ..types import (
    adapt_bool,
    convert_bool,
    adapt_int_list,
    convert_int_list,
    IntList,
)


class TestBoolType(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(
            ':memory:',
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_bool_adapter_false(self):
        self.assertEqual(b'0', adapt_bool(False))

    def test_bool_adapter_true(self):
        self.assertEqual(b'1', adapt_bool(True))

    def test_bool_converter_true(self):
        self.assertEqual(True, convert_bool(b'1'))

    def test_bool_converter_false(self):
        self.assertEqual(False, convert_bool(b'0'))

    def test_bool_insert_false_is_0(self):
        def converter(val):
            return val
        sqlite3.register_adapter(bool, adapt_bool)
        sqlite3.register_converter('BOOL', converter)
        with self.conn:
            self.conn.execute('CREATE TABLE test_table (test_bool BOOL, name TEXT)')
            self.conn.execute('INSERT INTO test_table VALUES (?, ?)', (False, 'test'))
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual(b'0', cursor.fetchone()['test_bool'])

    def test_bool_insert_true_is_1(self):
        def converter(val):
            return val
        sqlite3.register_adapter(bool, adapt_bool)
        sqlite3.register_converter('BOOL', converter)
        with self.conn:
            self.conn.execute('CREATE TABLE test_table (test_bool BOOL, name TEXT)')
            self.conn.execute('INSERT INTO test_table VALUES (?, ?)', (True, 'test'))
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual(b'1', cursor.fetchone()['test_bool'])

    def test_bool_select_true_is_true(self):
        sqlite3.register_adapter(bool, adapt_bool)
        sqlite3.register_converter('BOOL', convert_bool)
        with self.conn:
            self.conn.execute('CREATE TABLE test_table (test_bool BOOL, name TEXT)')
            self.conn.execute('INSERT INTO test_table VALUES (?, ?)', (True, 'test'))
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual(True, cursor.fetchone()['test_bool'])

    def test_bool_select_false_is_false(self):
        sqlite3.register_adapter(bool, adapt_bool)
        sqlite3.register_converter('BOOL', convert_bool)
        with self.conn:
            self.conn.execute('CREATE TABLE test_table (test_bool BOOL, name TEXT)')
            self.conn.execute('INSERT INTO test_table VALUES (?, ?)', (False, 'test'))
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual(False, cursor.fetchone()['test_bool'])


class TestIntIterType(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(
            ':memory:',
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_adapter_empty_list(self):
        self.assertEqual(b'', adapt_int_list([]))

    def test_adapter_list(self):
        self.assertEqual(b'1,2,3', adapt_int_list([1, 2, 3]))

    def test_adapter_negative_ints(self):
        self.assertEqual(b'1,-2,0', adapt_int_list([1, -2, 0]))

    def test_converter_empty(self):
        self.assertEqual([], convert_int_list(b''))

    def test_converter_positive_ints(self):
        self.assertEqual([1, 2, 3], [x for x in convert_int_list(b'1,2,3')])

    def test_converter_negative_ints(self):
        self.assertEqual([-1, 2, -3], [x for x in convert_int_list(b'-1,2,-3')])

    def test_insert_list(self):
        def converter(val):
            return val
        sqlite3.register_adapter(IntList, adapt_int_list)
        sqlite3.register_converter('INTLIST', converter)
        with self.conn:
            self.conn.execute(
                'CREATE TABLE test_table (test_intlist INTLIST, name TEXT)'
            )
            self.conn.execute(
                'INSERT INTO test_table VALUES (?, ?)',
                (IntList([1, 2]), 'test'),
            )
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual(b'1,2', cursor.fetchone()['test_intlist'])

    def test_insert_empty_list(self):
        def converter(val):
            return val
        sqlite3.register_adapter(IntList, adapt_int_list)
        sqlite3.register_converter('INTLIST', converter)
        with self.conn:
            self.conn.execute(
                'CREATE TABLE test_table (test_intlist INTLIST, name TEXT)'
            )
            self.conn.execute(
                'INSERT INTO test_table VALUES (?, ?)',
                (IntList([]), 'test'),
            )
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual(None, cursor.fetchone()['test_intlist'])

    def test_fetch_int_list(self):
        sqlite3.register_adapter(IntList, adapt_int_list)
        sqlite3.register_converter('INTLIST', convert_int_list)
        with self.conn:
            self.conn.execute(
                'CREATE TABLE test_table (test_intlist INTLIST, name TEXT)'
            )
            self.conn.execute(
                'INSERT INTO test_table VALUES (?, ?)',
                (IntList([1, 2, 3]), 'test'),
            )
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual([1, 2, 3], cursor.fetchone()['test_intlist'])

    def test_fetch_int_list_with_negatives(self):
        sqlite3.register_adapter(IntList, adapt_int_list)
        sqlite3.register_converter('INTLIST', convert_int_list)
        with self.conn:
            self.conn.execute(
                'CREATE TABLE test_table (test_intlist INTLIST, name TEXT)'
            )
            self.conn.execute(
                'INSERT INTO test_table VALUES (?, ?)',
                (IntList([-1, 0, -3]), 'test'),
            )
            cursor = self.conn.execute('SELECT * FROM test_table')
            self.assertEqual([-1, 0, -3], cursor.fetchone()['test_intlist'])
