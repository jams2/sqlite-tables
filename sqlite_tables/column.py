from collections import defaultdict
from typing import (
    DefaultDict,
    Any,
    Union,
    Optional,
)

from .exceptions import InvalidColumnConfiguration
from .enums import (
    SQLiteType,
    SQLiteConstraint,
    SQLiteConstant,
)
from .utils import SQLiteTemplate
from .types import IntList


class SQLiteColumn(object):
    column_def_template = SQLiteTemplate(
        '$column_name $type $null_constraint $default_constraint $unique_constraint'
    )
    foreign_key_constraint_template = SQLiteTemplate(
        'FOREIGN KEY ($column_name) REFERENCES $table_ref ($col_ref)'
    )
    trigger_expression_template = SQLiteTemplate(
        f'UPDATE $$table_name SET $column_name = $default_for_update WHERE '
        f'$$primary_key_col = old.$$primary_key_col'
    )

    @staticmethod
    def prepare_for_insert(value):
        return value

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
        self.default_for_update: Optional[str] = None

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

    def requires_trigger(self):
        return self.default_for_update is not None

    def validate_column_def_constraints(self) -> None:
        if self.is_primary_key and self.unique:
            raise InvalidColumnConfiguration(
                'column should have either is_primary_key or unique, not both'
            )
        if self.is_primary_key and self.default is not None:
            raise InvalidColumnConfiguration(
                'default value should not be specified for primary key columns'
            )

    def get_default_value_sql(self):
        return self.default

    def get_definition_subs(self) -> dict:
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
                f'{SQLiteConstraint.DEFAULT.value} {self.get_default_value_sql()}'
            )
        if not self.allow_null:
            substitutions['null_constraint'] = SQLiteConstraint.NOT_NULL.value
        return substitutions

    def definition_to_sql(self) -> str:
        return self.column_def_template.substitute(self.get_definition_subs())

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

    def get_trigger_expression_substitutions(self):
        return {
            'column_name': self.column_name,
            'default_for_update': self.default_for_update,
        }

    def trigger_expression_to_sql(self):
        return self.trigger_expression_template.substitute(
            self.get_trigger_expression_substitutions()
        )


class IntColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.INT, default=default, **kwargs)


class RealColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.REAL, default=default, **kwargs)


class TextColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.TEXT, default=default, **kwargs)

    def prepare_string_default(self, default_str: str) -> str:
        if default_str == "":
            return "''"
        if not default_str.startswith("'"):
            default_str = f"'{default_str}"
        if not default_str.endswith("'"):
            default_str = f"{default_str}'"
        return default_str

    def get_default_value_sql(self):
        return self.prepare_string_default(self.default)


class NumericColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Union[float, int, None] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.NUMERIC, default=default, **kwargs)


class DateTimeColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[str] = None,
        auto_now_insert: bool = False,
        auto_now_update: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            column_name,
            SQLiteType.TEXT,
            default=SQLiteConstant.CURRENT_TIMESTAMP.value if auto_now_insert else None,
            **kwargs,
        )
        if auto_now_update:
            self.default_for_update = SQLiteConstant.CURRENT_TIMESTAMP.value


class DateColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[str] = None,
        auto_now_insert: bool = False,
        auto_now_update: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            column_name,
            SQLiteType.TEXT,
            default=SQLiteConstant.CURRENT_DATE.value if auto_now_insert else None,
            **kwargs,
        )
        if auto_now_update:
            self.default_for_update = SQLiteConstant.CURRENT_DATE.value


class TimeColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[str] = None,
        auto_now_insert: bool = False,
        auto_now_update: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            column_name,
            SQLiteType.TEXT,
            default=SQLiteConstant.CURRENT_TIME.value if auto_now_insert else None,
            **kwargs,
        )
        if auto_now_update:
            self.default_for_update = SQLiteConstant.CURRENT_TIME.value


class BoolColumn(SQLiteColumn):
    def __init__(
        self,
        column_name: str,
        default: Optional[bool] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.BOOL, default=default, **kwargs)


class IntListColumn(SQLiteColumn):
    @staticmethod
    def prepare_for_insert(value):
        """sqlite3 checks the type of the object passed in to
        determine which adapter to call (if not a SQLite native type),
        so casting the list to an IntList here ensures the correct
        adapter is called.
        """
        return IntList(value)

    def __init__(
        self,
        column_name: str,
        default: Optional[bool] = None,
        **kwargs,
    ) -> None:
        super().__init__(column_name, SQLiteType.INT_LIST, default=default, **kwargs)
