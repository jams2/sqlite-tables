import sqlite3
import pathlib
from functools import wraps
from typing import (
    Optional,
    List,
    Dict,
    Any,
)

from .table import SQLiteTable
from .utils import SQLiteTemplate
from .exceptions import InvalidDatabaseConfiguration


def db_transaction(func):
    @wraps(func)
    def with_connection_context_manager(*args, **kwargs):
        if isinstance(args[0], sqlite3.Connection):
            db_connection = args[0]
        elif isinstance(args[0], SQLiteDatabase):
            db_connection = args[0].connection
        else:
            raise ValueError(
                'First positional argument to function wrapped with "db_transaction" '
                'must be of type sqlite3.Connection'
            )
        with db_connection:
            return func(*args, **kwargs)
    return with_connection_context_manager


class SQLiteDatabase(object):
    insert_template = SQLiteTemplate(
        'INSERT INTO $table ($columns) VALUES ($value_template)'
    )

    def __init__(
        self,
        path: Optional[pathlib.Path] = None,
        tables: List[SQLiteTable] = None,
        connection: Optional[sqlite3.Connection] = None,
    ):
        self.path = path
        if path is not None and connection is not None:
            raise InvalidDatabaseConfiguration(
                'Specify either connection object or path'
            )
        elif connection is not None:
            self.connection = connection
        else:
            self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.tables = tables
        self.existing_tables = self.get_existing_tables()

    @db_transaction
    def get_existing_tables(self):
        return [x[0] for x in self.connection.execute(
            'SELECT name FROM sqlite_master WHERE type = :type_arg',
            {'type_arg': 'table'},
        )]

    @db_transaction
    def do_creation(self) -> None:
        for table in self.tables:
            self.connection.execute(table.schema_to_sql())
            for trigger_def in table.triggers_to_sql():
                self.connection.execute(trigger_def)

    @db_transaction
    def insert(self, table: str, value_dict: Dict[str, Any]):
        insert_statement = self.insert_template.substitute({
            'table': table,
            'columns': ', '.join(value_dict.keys()),
            'value_template': ', '.join(f':{x}' for x in value_dict.keys()),
        })
        self.connection.execute(insert_statement, value_dict)
