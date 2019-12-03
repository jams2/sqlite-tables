from collections import defaultdict
from typing import (
    DefaultDict,
    Any,
    Union,
    Optional,
)

from .exceptions import InvalidColumnConfiguration
from .utils import (
    SQLiteType,
    SQLiteTemplate,
    SQLiteConstraint,
)


CASCADE = 'CASCADE'


class DatabaseColumn(object):
    column_def_template = SQLiteTemplate(
        '$column_name $type $null_constraint $default_constraint $unique_constraint'
    )
    foreign_key_constraint_template = SQLiteTemplate(
        'FOREIGN KEY ($column_name) REFERENCES $table_ref ($col_ref)'
    )

    def __init__(
        self,
        column_name: str,
        sqlite_type: SQLiteType,
        allow_null: bool = True,
        default: Optional[Any] = None,
        is_foreign_key: bool = False,
        fk_column_ref: Optional[str] = None,
        fk_table_ref: Optional[str] = None,
        is_primary_key: bool = False,
        unique: bool = False,
    ) -> None:
        self.column_name = column_name
        self.sqlite_type = sqlite_type
        self.allow_null = allow_null
        self.default = default
        self.is_foreign_key = is_foreign_key
        self.fk_column_ref = fk_column_ref
        self.fk_table_ref = fk_table_ref
        self.is_primary_key = is_primary_key
        self.unique = unique

    def __repr__(self):
        template = (
            '{!s}({!r}, {!r}, allow_null={!r}, default={!r}, is_foreign_key={!r}, '
            'fk_column_ref={!r}, fk_table_ref={!r}, is_primary_key={!r}, unique={!r})'
        )
        return template.format(
            self.__class__.__name__,
            self.column_name,
            self.sqlite_type,
            self.allow_null,
            self.default,
            self.is_foreign_key,
            self.fk_column_ref,
            self.fk_table_ref,
            self.is_primary_key,
            self.unique,
        )

    def __str__(self):
        return '<{!s}: {!r}>'.format(self.__class__.__name__, self.column_name)

    def validate_column_def_constraints(self) -> None:
        if self.is_primary_key and self.unique:
            raise InvalidColumnConfiguration(
                'column should have either is_primary_key or unique, not both'
            )
        if self.is_primary_key and self.default is not None:
            raise InvalidColumnConfiguration(
                'default value should not be specified for primary key columns'
            )

    def get_def_substitutions(self) -> dict:
        self.validate_column_def_constraints()
        substitutions: DefaultDict[str, str] = defaultdict(str)
        substitutions['column_name'] = self.column_name
        substitutions['type'] = self.sqlite_type.value
        if self.is_primary_key:
            substitutions['unique_constraint'] = SQLiteConstraint.PRIMARY_KEY.value
        elif self.unique:
            substitutions['unique_constraint'] = SQLiteConstraint.UNIQUE.value
        if self.default is not None:
            substitutions['default_constraint'] = (
                f'{SQLiteConstraint.DEFAULT.value} {self.default}'
            )
        if not self.allow_null:
            substitutions['null_constraint'] = SQLiteConstraint.NOT_NULL.value
        return substitutions

    def definition_to_sql(self) -> str:
        return self.column_def_template.substitute(self.get_def_substitutions())

    def get_fk_constraint_substitutions(self) -> dict:
        substitutions = {
            'column_name': self.column_name,
            'table_ref': self.fk_table_ref,
            'col_ref': self.fk_column_ref,
        }
        for key in ('table_ref', 'col_ref'):
            if substitutions.get(key) is None:
                raise InvalidColumnConfiguration(
                    f'{key} can not be None if is_foreign_key=True'
                )
        return substitutions

    def fk_constraint_to_sql(self) -> str:
        return self.foreign_key_constraint_template.substitute(
            self.get_fk_constraint_substitutions()
        )


class IntColumn(DatabaseColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.INT, default=default, **kwargs)


class RealColumn(DatabaseColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.REAL, default=default, **kwargs)


class TextColumn(DatabaseColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[str] = None,
        **kwargs,
    ) -> None:
        if default is not None:
            default = self.add_quote_marks_to_string_default(default)
        super().__init__(column_name, SQLiteType.TEXT, default=default, **kwargs)

    def add_quote_marks_to_string_default(self, default_str: str) -> str:
        if not default_str.startswith('"'):
            default_str = f'"{default_str}'
        if not default_str.endswith('"'):
            default_str = f'{default_str}"'
        return default_str


class NumericColumn(DatabaseColumn):
    def __init__(
        self,
        column_name: str,
        default: Union[float, int, None] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.NUMERIC, default=default, **kwargs)
