from __future__ import annotations

import pickle
import sqlite3
from sqlite3 import Connection, Error

import lz4.frame

_DB_NAME: str = r"_gen_storage.db"
_conn: Connection


def _create_table():
    sql = """CREATE TABLE IF NOT EXISTS storage (
                md5 TEXT PRIMARY KEY NOT NULL
            );"""
    try:
        c = _conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def _create_connection():
    """create a database connection to a SQLite database"""

    global _conn

    try:  # tests if connection is already established
        _conn.cursor()
        return  # return if it is
    except:
        pass

    try:
        _conn = sqlite3.connect(_DB_NAME)
        _conn.execute("PRAGMA auto_vacuum = FULL")
        _create_table()
    except Error as e:
        print(e)


def exists_column(column_name: str) -> bool:
    _create_connection()
    cur = _conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM pragma_table_info('storage') where name='{column_name}';")
    return cur.fetchone()[0] == 1


def insert_object(column_name: str, md5: str, object: object, override: bool = True, compress: bool = False) -> None:
    if column_name == "md5":
        raise Exception(f"invalid name: {column_name}")

    _create_connection()
    cur = _conn.cursor()

    if not exists_column(column_name):
        cur.execute(f"ALTER TABLE storage ADD COLUMN {column_name} BLOB")

    sql = f"INSERT OR IGNORE INTO storage (md5, {column_name}) VALUES (?, ?)"
    data = pickle.dumps(object)
    if compress:
        data = lz4.frame.compress(data)
    cur.execute(sql, (md5, data))

    if override:
        sql = f"UPDATE storage SET {column_name} = ? WHERE md5 = ?"
        cur.execute(sql, (data, md5))

    _conn.commit()


def select_object(column_name: str, md5: str, default_value: object = None, decompress: bool = False) -> object:
    if column_name == "md5":
        raise Exception(f"invalid name: {column_name}")

    _create_connection()
    cur = _conn.cursor()

    try:
        cur.execute(f"SELECT {column_name} FROM storage WHERE md5=?", (md5,))
        data = cur.fetchone()[0]
        if decompress:
            data = lz4.frame.decompress(data)
        return pickle.loads(data)
    except:
        return default_value


def drop_column(column_name: str) -> None:
    if column_name == "md5":
        raise Exception(f"invalid name: {column_name}")

    _create_connection()
    cur = _conn.cursor()

    try:
        cur.execute(f"ALTER TABLE storage DROP COLUMN {column_name}")
        _conn.commit()
    except:
        pass


def delete_row(md5: str) -> None:
    _create_connection()
    cur = _conn.cursor()

    try:
        cur.execute(f"DELETE FROM storage WHERE md5 = {md5}")
        _conn.commit()
    except:
        pass
