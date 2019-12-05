import sqlite3
from collections import defaultdict
import itertools
from typing import (
    Optional,
    Union,
    List,
    Tuple,
    DefaultDict,
    Generator,
)

from .exceptions import InvalidTableConfiguration
from .column import DatabaseColumn
from .utils import (
    SQLiteTemplate,
    SQLiteConstraint,
)


class DatabaseTable(object):
    schema_template = SQLiteTemplate(
        'CREATE TABLE $exists $table_name ($column_defs)'
    )
    unique_template = SQLiteTemplate('UNIQUE ($fields)')
    trigger_template = SQLiteTemplate(
        'CREATE TRIGGER $trigger_name $when $event ON $table_name BEGIN $expr; END'
    )

    def __init__(
        self,
        table_name: str,
        columns: Union[List[DatabaseColumn], Tuple[DatabaseColumn], tuple] = (),
        unique_together: Union[Tuple[str], Tuple[Tuple], Tuple] = (),
        raise_exists_error: bool = False,
        connection: Optional[sqlite3.Connection] = None,
    ):
        self.table_name = table_name
        self.columns = columns
        self.column_names = {x.column_name for x in columns}
        self.unique_together = unique_together
        self.raise_exists_error = raise_exists_error
        self.foreign_key_columns = filter(lambda x: x.is_foreign_key, columns)
        self.connection = connection
        try:
            self.primary_key_col = list(
                filter(lambda x: x.is_primary_key, self.columns)
            )[0]
        except IndexError:
            self.primary_key_col = None

    def __repr__(self) -> str:
        template = (
            '{!s}({!r}, columns={!r}, unique_together={!r}, raise_exists_error={!r})'
        )
        return template.format(
            self.__class__.__name__,
            self.table_name,
            self.columns,
            self.unique_together,
            self.raise_exists_error,
        )

    def __str__(self) -> str:
        return '<{!s}: {!r}>'.format(self.__class__.__name__, self.table_name)

    def get_primary_key_col_name(self) -> str:
        if self.primary_key_col is not None:
            return self.primary_key_col.column_name
        return 'rowid'

    def validate_columns(self) -> None:
        if len(self.columns) > len(self.column_names):
            raise InvalidTableConfiguration('Column names must be unique')
        if len(self.columns) == 0:
            raise InvalidTableConfiguration('Cannot create table without columns')

    def get_unique_constraints_sql(self) -> Union[Generator, tuple]:
        try:
            if isinstance(self.unique_together[0], str):
                unique_sets: Tuple = (self.unique_together,)
            else:
                unique_sets = self.unique_together
        except IndexError:
            return ()
        return (
            self.unique_template.substitute(fields=', '.join(x)) for x in unique_sets
        )

    def get_foreign_key_constraints_sql(self) -> Generator:
        return (x.fk_constraint_to_sql() for x in self.foreign_key_columns)

    def get_column_defs_sql(self) -> str:
        return ', '.join(
            itertools.chain(
                (x.definition_to_sql() for x in self.columns),
                self.get_foreign_key_constraints_sql(),
                self.get_unique_constraints_sql(),
            )
        )

    def get_schema_definition_subs(self) -> dict:
        self.validate_columns()
        substitutions: DefaultDict[str, str] = defaultdict(str)
        substitutions['table_name'] = self.table_name
        substitutions['column_defs'] = self.get_column_defs_sql()
        if not self.raise_exists_error:
            substitutions['exists'] = SQLiteConstraint.IF_NOT_EXISTS.value
        return substitutions

    def schema_to_sql(self) -> str:
        return self.schema_template.substitute(self.get_schema_definition_subs())

    def triggers_to_sql(self) -> List[str]:
        triggers = []
        for column in self.columns:
            if column.default_for_update is not None:
                expr_template = SQLiteTemplate(column.trigger_expression_to_sql())
                substitutions = {
                    'expr': expr_template.substitute(
                        {
                            'primary_key_col': self.get_primary_key_col_name(),
                            'table_name': self.table_name,
                        },
                    ),
                    'trigger_name': f'{self.table_name}_{column.column_name}_update',
                    'when': 'AFTER',
                    'event': 'UPDATE',
                    'table_name': self.table_name,
                }
                triggers.append(self.trigger_template.substitute(substitutions))
        return triggers
