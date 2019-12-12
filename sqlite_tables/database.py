import sqlite3
import pathlib
from functools import wraps
from typing import (
    Callable,
    Optional,
    List,
    Dict,
    Any,
    Tuple,
)

from .enums import SQLiteType
from .table import SQLiteTable
from .utils import SQLiteTemplate
from .exceptions import InvalidDatabaseConfiguration
from .types import (
    IntList,
    adapt_bool,
    convert_bool,
    adapt_int_list,
    convert_int_list,
)


def db_transaction(func):
    @wraps(func)
    def with_connection_context_manager(*args, **kwargs):
        if isinstance(args[0], sqlite3.Connection):
            db_connection = args[0]
        elif hasattr(args[0], 'connection'):
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
        'INSERT INTO $table_name ($column_names) VALUES ($value_template)'
    )
    default_adapters = (
        (bool, adapt_bool),
        (IntList, adapt_int_list),
    )
    default_converters = (
        (SQLiteType.BOOL, convert_bool),
        (SQLiteType.INT_LIST, convert_int_list),
    )

    def __init__(
        self,
        path: Optional[pathlib.Path] = None,
        tables: List[SQLiteTable] = [],
        connection: Optional[sqlite3.Connection] = None,
        adapters: Tuple = (),
        converters: Tuple = (),
    ):
        self.path = path
        if path is not None and connection is not None:
            raise InvalidDatabaseConfiguration(
                'Specify either connection object or path'
            )
        elif connection is not None:
            self.connection = connection
        else:
            self.register_adapters(self.default_adapters + adapters)
            self.register_converters(self.default_converters + converters)
            self.connection = sqlite3.connect(
                path,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
        self.connection.row_factory = sqlite3.Row
        self.tables = {table.table_name: table for table in tables}
        self.existing_tables = self.get_existing_tables()

    def register_adapters(self, adapters: Tuple[Tuple[Any, Callable]]) -> None:
        for python_type, adapter_func in adapters:
            sqlite3.register_adapter(python_type, adapter_func)

    def register_converters(self, converters: Tuple[Tuple[str, Callable]]) -> None:
        for declared_type, converter_func in converters:
            sqlite3.register_converter(declared_type, converter_func)

    @db_transaction
    def get_existing_tables(self):
        return [x[0] for x in self.connection.execute(
            'SELECT name FROM sqlite_master WHERE type = :type_arg',
            {'type_arg': 'table'},
        )]

    @db_transaction
    def do_creation(self) -> None:
        for table in self.tables.values():
            self.connection.execute(table.schema_to_sql())
            for trigger_def in table.triggers_to_sql():
                self.connection.execute(trigger_def)

    @db_transaction
    def insert(self, table_name: str, value_dict: Dict[str, Any]):
        try:
            table = self.tables[table_name]
        except KeyError:
            raise ValueError(f'Database has no table: "{table_name}"')
        for column_name, value in value_dict.items():
            try:
                column = table.columns[column_name]
            except KeyError:
                raise ValueError(f'Table "{table_name}" has no Column "{column_name}"')
            value_dict[column_name] = column.prepare_for_insert(value)
        insert_statement = self.insert_template.substitute({
            'table_name': table_name,
            'column_names': ', '.join(value_dict.keys()),
            'value_template': ', '.join(f':{x}' for x in value_dict.keys()),
        })
        self.connection.execute(insert_statement, value_dict)
