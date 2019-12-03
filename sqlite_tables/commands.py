import sqlite3
from datetime import datetime
from typing import (
    Dict,
    Union,
)

from .utils import db_transaction


@db_transaction
def insert_campaign(
    conn: sqlite3.Connection,
    values: Dict[str, Union[str, datetime]],
) -> None:
    update_timestr = datetime.now().isoformat()
    values.update({'created': update_timestr, 'updated': update_timestr})
    conn.execute(
        '''INSERT INTO campaign (title, notes, created, updated)
        VALUES (:title, :notes, :created, :updated)''',
        values,
    )


@db_transaction
def insert_encounter(
    conn: sqlite3.Connection,
    values: Dict[str, Union[str, datetime]],
) -> None:
    update_timestr = datetime.now()
    values.update({'created': update_timestr, 'updated': update_timestr})
    conn.execute(
        '''INSERT INTO encounter (campaign_id, title, notes, created, updated)
        VALUES (:campaign_id, :title, :notes, :created, :updated)''',
        values,
    )


def prepare_values(values):
    return


@db_transaction
def do_insert(
    conn: sqlite3.Connection,
    table: str,
    insert_dict: dict,
) -> None:
    columns = ', '.join(insert_dict.keys())
    values = ', '.join(insert_dict.values())
