from __future__ import annotations
import math
import sqlite3
from tqdm import tqdm
from osuclasses import Song, Collection
import controller as controller
from timeslice import Timeslice, Note
import songdb
import useless

OSU_DB_FILE: str = "C:\Games\osu!\osu!.db"
OSU_COLLECTION_FILE: str = "C:\Games\osu!\collection.db"
OSU_SONGS_FOLDER: str = "E:\Games\osu!\Songs"
# either change this to True or delte _gen_osu!.db to rescan original osu!.db
RESCAN_OSU_DB: bool = False

collection: Collection = Collection()


def on_start() -> None:
    """
        use this method to read collection or initialize other variables
    """
    # collection.read(OSU_COLLECTION_FILE)


def songs_filter(song_info: Song.Info) -> bool:
    """ 
        specify if given song information should be kept in pool of songs
        song_info is what's available via osu!.db
        make sure to return True for songs to keep
    """

    # return song_info.gameplay_mode == 3 and song_info.md5_hash in collection.collections["🎹 LN"]  # only accept songs in collection
    # return any(song_info.md5_hash in md5s for md5s in collection.collections.values()) check if song is present in any collection

    if song_info.gameplay_mode != 3:  # 3 is mania
        return False

    if song_info.circle_size != 7:  # filter out all non-7k
        return False

    if song_info.folder_name.startswith("- # IIDX 24 SINOBUZ"):
        return False

    if song_info.folder_name.startswith("[_BMS_]"):
        return False

    return True  # make sure to return True for all other songs


def songs_apply(encoded_song_data: str, song_info: Song.Info):
    """ 
        this method gets called for every song that got accepted by songs_filter
        song: Song = songdb.decode_to_song(encoded_song_data, song_info)
        to decode it
    """

    song: Song = songdb.decode_to_song(encoded_song_data, song_info)

    # use tqdm.write() instead of print() here qdm.write(song.info.song_title)

    # useless.print_slices_as_beatmap(slices[:10])

    # if "insert collection name here" not in collection.collections:
    #     collection.collections["insert collection name here"] = [] # create empty array if it doesn't exist yet
    # collection.collections["insert collection name here"].append(song.info.md5_hash) # add md5 to collection

    # tqdm.write(f"{song.info.song_title} [{song.info.difficulty}]")

    # slices: list[Timeslice] = Timeslice.generate_timeslices(song) for mania


def on_end() -> None:
    """ 
        use this to write collections to file
    """
    # collection.write(osu_collection_file) # OVERWRITE(!) collection file


if __name__ == "__main__":
    controller.start()
