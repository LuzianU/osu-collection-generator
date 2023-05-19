from __future__ import annotations
import mmap
import buffer_io as buffer_io
import sqlite3
from tqdm import tqdm
import main

DB_NAME: str = r"_gen_osu!.db"


def select_all_song_info() -> sqlite3.Cursor:
    sql = sqlite3.connect(DB_NAME)
    c = sql.cursor()
    c.execute(
        ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='song_info' ''')
    if c.fetchone()[0] == 0:
        print("no song info found in db")
        return
    c.execute(
        "SELECT * FROM song_info ORDER BY md5_hash ASC;"
    )
    return c


def create_db(filename):
    sql = sqlite3.connect(DB_NAME)
    c = sql.cursor()
    c.execute(
        ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='song_info' ''')
    if c.fetchone()[0] > 0:
        if main.RESCAN_OSU_DB:
            sql.execute("DROP TABLE song_info")
        else:
            return
    sql.execute("""
        CREATE TABLE song_info (
            artist TEXT,
            artist_unicode TEXT,
            title TEXT,
            title_unicode TEXT,
            mapper TEXT,
            difficulty TEXT,
            audio_file TEXT,
            md5_hash TEXT,
            map_file TEXT,
            ranked_status INTEGER,
            num_hitcircles INTEGER,
            num_sliders INTEGER,
            num_spinners INTEGER,
            last_modified INTEGER,
            approach_rate NUMERIC,
            circle_size NUMERIC,
            hp_drain NUMERIC,
            overall_difficulty NUMERIC,
            slider_velocity NUMERIC,
            drain_time INTEGER,
            total_time INTEGER,
            preview_time INTEGER,
            beatmap_id INTEGER,
            beatmap_set_id INTEGER,
            thread_id INTEGER,
            grade_stadard INTEGER,
            grade_taiko INTEGER,
            grade_ctb INTEGER,
            grade_mania INTEGER,
            local_offset INTEGER,
            stack_leniency NUMERIC,
            gameplay_mode INTEGER,
            song_source TEXT,
            song_tags TEXT,
            online_offset INTEGER,
            font TEXT,
            is_unplayed INTEGER,
            last_played INTEGER,
            is_osz2 INTEGER,
            folder_name TEXT,
            last_checked INTEGER,
            ignore_sounds INTEGER,
            ignore_skin INTEGER,
            disable_storyboard INTEGER,
            disable_video INTEGER,
            visual_override INTEGER,
            last_modified2 INTEGER,
            mania_speed INTEGER,
            star_rating_osu REAL,
            star_rating_taiko REAL,
            star_rating_ctb REAL,
            star_rating_mania REAL
        );
    """)

    with open(filename, "rb") as f:
        # File is open read-only
        db = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        version = buffer_io.read_uint(db)
        folder_count = buffer_io.read_uint(db)
        account_unlocked = buffer_io.read_bool(db)

        buffer_io.read_uint(db)
        buffer_io.read_uint(db)
        name = buffer_io.read_string(db)
        num_beatmaps = buffer_io.read_uint(db)
        for _ in tqdm(range(num_beatmaps), desc="reading osu!.db"):
            artist = buffer_io.read_string(db)
            artist_unicode = buffer_io.read_string(db)
            song_title = buffer_io.read_string(db)
            song_title_unicode = buffer_io.read_string(db)
            mapper = buffer_io.read_string(db)
            difficulty = buffer_io.read_string(db)
            audio_file = buffer_io.read_string(db)
            md5_hash = buffer_io.read_string(db)
            map_file = buffer_io.read_string(db)
            ranked_status = buffer_io.read_ubyte(db)
            num_hitcircles = buffer_io.read_ushort(db)
            num_sliders = buffer_io.read_ushort(db)
            num_spinners = buffer_io.read_ushort(db)
            last_modified = buffer_io.read_ulong(db)
            approach_rate = buffer_io.read_float(db)
            circle_size = buffer_io.read_float(db)
            hp_drain = buffer_io.read_float(db)
            overall_difficulty = buffer_io.read_float(db)
            slider_velocity = buffer_io.read_double(db)

            i = buffer_io.read_uint(db)
            # db.seek(i * 14, 1)
            star_rating_osu = 0
            sr_counter = 0
            if i > 0:
                while sr_counter < i:
                    sr_counter += 1
                    (mod, sr) = buffer_io.read_int_double(db)
                    if mod == 0:
                        star_rating_osu = sr
                        break
                db.seek((i-sr_counter) * 14, 1)

            i = buffer_io.read_uint(db)
            # db.seek(i * 14, 1)
            star_rating_taiko = 0
            sr_counter = 0
            if i > 0:
                while sr_counter < i:
                    sr_counter += 1
                    (mod, sr) = buffer_io.read_int_double(db)
                    if mod == 0:
                        star_rating_taiko = sr
                        break
                db.seek((i-sr_counter) * 14, 1)
            i = buffer_io.read_uint(db)
            # db.seek(i * 14, 1)
            star_rating_ctb = 0
            sr_counter = 0
            if i > 0:
                while sr_counter < i:
                    sr_counter += 1
                    (mod, sr) = buffer_io.read_int_double(db)
                    if mod == 0:
                        star_rating_ctb = sr
                        break
                db.seek((i-sr_counter) * 14, 1)

            i = buffer_io.read_uint(db)
            # db.seek(i * 14, 1)
            star_rating_mania = 0
            sr_counter = 0
            if i > 0:
                while sr_counter < i:
                    sr_counter += 1
                    (mod, sr) = buffer_io.read_int_double(db)
                    if mod == 0:
                        star_rating_mania = sr
                        break
                db.seek((i-sr_counter) * 14, 1)

            drain_time = buffer_io.read_uint(db)
            total_time = buffer_io.read_uint(db)
            preview_time = buffer_io.read_uint(db)
            # skip timing points
            i = buffer_io.read_uint(db)
            db.seek(i * 17, 1)
            # for _ in range(buffer.read_uint(db)):
            #    buffer.read_timing_point(db)
            beatmap_id = buffer_io.read_uint(db)
            beatmap_set_id = buffer_io.read_uint(db)
            thread_id = buffer_io.read_uint(db)
            grade_standard = buffer_io.read_ubyte(db)
            grade_taiko = buffer_io.read_ubyte(db)
            grade_ctb = buffer_io.read_ubyte(db)
            grade_mania = buffer_io.read_ubyte(db)
            local_offset = buffer_io.read_ushort(db)
            stack_leniency = buffer_io.read_float(db)
            gameplay_mode = buffer_io.read_ubyte(db)
            song_source = buffer_io.read_string(db)
            song_tags = buffer_io.read_string(db)
            online_offset = buffer_io.read_ushort(db)
            title_font = buffer_io.read_string(db)
            is_unplayed = buffer_io.read_bool(db)
            last_played = buffer_io.read_ulong(db)
            is_osz2 = buffer_io.read_bool(db)
            folder_name = buffer_io.read_string(db)
            last_checked = buffer_io.read_ulong(db)
            ignore_sounds = buffer_io.read_bool(db)
            ignore_skin = buffer_io.read_bool(db)
            disable_storyboard = buffer_io.read_bool(db)
            disable_video = buffer_io.read_bool(db)
            visual_override = buffer_io.read_bool(db)
            last_modified2 = buffer_io.read_uint(db)
            scroll_speed = buffer_io.read_ubyte(db)
            sql.execute(
                "INSERT INTO song_info VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (artist, artist_unicode, song_title, song_title_unicode, mapper, difficulty, audio_file, md5_hash, map_file, ranked_status, num_hitcircles, num_sliders, num_spinners, last_modified, approach_rate, circle_size, hp_drain, overall_difficulty, slider_velocity, drain_time, total_time, preview_time, beatmap_id, beatmap_set_id, thread_id, grade_standard, grade_taiko,
                 grade_ctb, grade_mania, local_offset, stack_leniency, gameplay_mode, song_source, song_tags, online_offset, title_font, is_unplayed, last_played, is_osz2, folder_name, last_checked, ignore_sounds, ignore_skin, disable_storyboard, disable_video, visual_override, last_modified2, scroll_speed, star_rating_osu, star_rating_taiko, star_rating_ctb, star_rating_mania)
            )
    sql.commit()
    sql.close()
