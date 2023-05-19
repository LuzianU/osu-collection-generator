from __future__ import annotations
import sqlite3
from sqlite3 import Cursor, Error
import zlib
import json
from osuclasses import Song

DB_NAME: str = r"_gen_songs.db"


def _create_table():
    sql = """CREATE TABLE IF NOT EXISTS songs (
                md5 TEXT PRIMARY KEY NOT NULL,
                song BLOB
            );"""
    try:
        c = _conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def create_connection():
    """ create a database connection to a SQLite database """
    try:
        global _conn
        _conn = sqlite3.connect(DB_NAME)
        _create_table()
    except Error as e:
        print(e)


def insert_song_dict(song_dict: dict):
    sql = ''' INSERT OR IGNORE INTO songs(md5,song)
              VALUES(?,?) '''
    cur = _conn.cursor()

    msg = json.dumps(song_dict, ensure_ascii=False)
    compressed = zlib.compress(msg.encode("utf-8"))

    cur.execute(sql, (song_dict["md5"], compressed))
    _conn.commit()
    return cur.lastrowid


def select_song(song_info: Song.Info):
    cur = _conn.cursor()
    cur.execute("SELECT song FROM songs WHERE md5=?", (song_info.md5_hash,))

    data = cur.fetchone()

    if data is None:
        return None

    return decode_to_song(data[0], song_info)


def select_songs(md5s: list[str]) -> Cursor:
    cur = _conn.cursor()
    return cur.execute("SELECT song FROM songs WHERE md5 IN ({0})".format(', '.join('?' for _ in md5s)), md5s)


def decode_to_song(data: str, song_info: Song.Info) -> Song:
    decompressed = zlib.decompress(data).decode("utf-8")
    dict = json.loads(decompressed)
    return Song(song_info, dict)


def select_md5s() -> set:
    cur = _conn.cursor()
    cur.execute("SELECT md5 FROM songs")

    data = cur.fetchall()

    if data is None:
        return None

    return set([x[0] for x in data])
