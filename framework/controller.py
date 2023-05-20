from __future__ import annotations
from sqlite3 import Cursor
import cProfile
import main
import osudb as osudb
import songdb as songdb
import dotosuparser as dotosuparser
from osuclasses import Song
from collections import deque
from pathlib import Path
from tqdm import tqdm


def start():
    main.on_start()

    # generate _gen_osu!.db from osu!.db if it's missing or main.RESCAN_OSU_DB == True
    osudb.create_db(main.OSU_DB_FILE)

    rows: Cursor = osudb.select_all_song_info()
    total_rows = sum(1 for _ in rows)  # meh
    rows: Cursor = osudb.select_all_song_info()

    # establish connection of compressed .osu file database
    songdb.create_connection()

    known_md5s: set = songdb.select_md5s()
    filtered_md5s: deque = deque()

    for row in tqdm(rows, desc="reading .osu files", total=total_rows):
        song_info: Song.Info = Song.Info(*row)

        if not song_info.md5_hash:
            continue

        # skip if filter returns None or False
        if not main.songs_filter(song_info):
            continue

        # read .osu file into database if it's not there already
        if song_info.md5_hash not in known_md5s:
            f = Path(main.OSU_SONGS_FOLDER, song_info.folder_name,
                     song_info.map_file)

            if not f.exists():
                continue

            song_dict: dict = dotosuparser.read_osu(f)

            # if error:
            #   tqdm.write(f"file might have parsed incorrectly: \{song_info.folder_name}\{song_info.map_file}")

            if song_dict["md5"] != song_info.md5_hash:
                # if they mismatch, save both
                tqdm.write(
                    f"md5 mismatch: \{song_info.folder_name}\{song_info.map_file}")
                songdb.insert_song_dict(song_dict)
                song_dict["md5"] = song_info.md5_hash
            songdb.insert_song_dict(song_dict)

        filtered_md5s.append(song_info.md5_hash)

    tqdm.write(f"{len(filtered_md5s)} songs accepted")

    filtered_md5s = sorted(filtered_md5s)
    filtered_md5s = deque(filtered_md5s[5:])

    # this is this scuffed to not have to load all songs into memory all at once and rather iterate over them
    rows: Cursor = osudb.select_all_song_info()
    it = iter(songdb.select_songs(filtered_md5s))

    with tqdm(total=len(filtered_md5s), desc="applying") as pbar:
        for row in rows:
            if not filtered_md5s:
                break

            song_info: Song.Info = Song.Info(*row)

            if filtered_md5s[0] > song_info.md5_hash:
                continue

            filtered_md5s.popleft()  # pop md5

            data = next(it)[0]

            main.songs_apply(data, song_info)

            pbar.update(1)

    main.on_end()
