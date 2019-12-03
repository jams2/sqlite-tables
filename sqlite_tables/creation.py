import sqlite3

from .utils import db_transaction


def get_m2m_creation_kwargs(
    join_table_name: str,
    table_1: str,
    table_2: str,
) -> dict:
    return {
        'join_table_name': join_table_name,
        'table_1': table_1,
        'table_2': table_2,
        'table_1_ref': f'{table_1}_id',
        'table_2_ref': f'{table_2}_id',
    }


@db_transaction
def create_m2m_table(
    conn: sqlite3.Connection,
    join_table_name: str,
    table_1: str,
    table_2: str,
) -> None:
    values = get_m2m_creation_kwargs(join_table_name, table_1, table_2)
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS {join_table_name} (
        {table_1_ref} INT NOT NULL,
        {table_2_ref} INT NOT NULL,
        FOREIGN KEY ({table_1_ref}) REFERENCES {table_1} (id),
        FOREIGN KEY ({table_2_ref}) REFERENCES {table_2} (id),
        UNIQUE ({table_1_ref}, {table_2_ref})
        )'''.format_map(values)
    )


@db_transaction
def create_weapon_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS weapon (
        id INT PRIMARY KEY,
        name TEXT NOT NULL,
        cost TEXT NOT NULL,
        damage TEXT NOT NULL,
        damage_type INT NOT NULL,
        weight INT NOT NULL,
        is_melee INT NOT NULL,
        is_ranged INT NOT NULL,
        requires_ammo INT NOT NULL,
        is_finesse INT NOT NULL,
        is_heavy INT NOT NULL,
        is_light INT NOT NULL,
        range_short INT,
        range_long INT,
        has_reach INT NOT NULL,
        is_special INT NOT NULL,
        can_be_thrown INT NOT NULL,
        is_two_handed INT NOT NULL,
        is_versatile INT NOT NULL,
        versatile_damage TEXT,
        is_silver INT NOT NULL,
        description TEXT,
        notes TEXT
        )'''
    )


@db_transaction
def create_spell_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS spell (
        id INT PRIMARY KEY,
        casting_time TEXT NOT NULL,
        range TEXT NOT NULL,
        components TEXT NOT NULL,
        duration TEXT NOT NULL,
        description TEXT NOT NULL,
        notes TEXT
        )'''
    )


@db_transaction
def create_feat_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS feat (
        feat_id INT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL
        )'''
    )


@db_transaction
def create_character_table(conn: sqlite3.Connection) -> None:
    # add foreign keys
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS character (
        id INT PRIMARY KEY,
        is_pc INT NOT NULL,
        name TEXT NOT NULL,
        race_id INT NOT NULL,
        size INT NOT NULL,
        type INT,
        alignment INT,
        class INT,
        level INT,
        ac INT,
        initiative INT,
        speed INT,
        speed_fly INT,
        speed_climb INT,
        speed_swim INT,
        speed_burrow INT,
        hp_max INT,
        hp_current INT,
        hp_temp INT,
        hit_dice TEXT,
        death_save_success INT,
        death_save_failure INT,
        xp INT,
        strength INT,
        dexterity INT,
        constitution INT,
        intelligence INT,
        wisdom INT,
        charisma INT,
        challenge_rating REAL,
        challenge_xp INT,
        proficiency_bonus INT,
        inspiration INT,
        cp INT,
        sp INT,
        ep INT,
        gp INT,
        pp INT
        )'''
    )


@db_transaction
def create_campaign_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS campaign (
        id INT PRIMARY KEY,
        title TEXT NOT NULL,
        notes TEXT,
        created TEXT NOT NULL,
        updated TEXT NOT NULL
        )'''
    )


@db_transaction
def create_encounter_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS encounter (
        id INT PRIMARY KEY,
        campaign_id INT,
        title TEXT,
        notes TEXT,
        created TEXT,
        updated TEXT,
        FOREIGN KEY (campaign_id) REFERENCES campaign (id)
        )'''
    )


def do_db_setup(conn: sqlite3.Connection) -> None:
    create_campaign_table(conn)
    create_character_table(conn)
    create_encounter_table(conn)
    create_feat_table(conn)
    create_spell_table(conn)
    create_weapon_table(conn)
    create_m2m_table(conn, 'campaign_characters', 'campaign', 'character')
    create_m2m_table(conn, 'encounter_characters', 'encounter', 'character')
    create_m2m_table(conn, 'character_feats', 'character', 'feat')
    create_m2m_table(conn, 'character_spells', 'character', 'spell')
    create_m2m_table(conn, 'character_weapons', 'character', 'weapon')
