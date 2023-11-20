from __future__ import annotations

import controller as controller
import songdb
from osuclasses import Collection, Song

import storagedb
from timeslice import Note, Timeslice

OSU_DB_FILE: str = r"C:\Games\osu!\osu!.db"
OSU_COLLECTION_FILE: str = r"C:\Games\osu!\collection.db"
OSU_SONGS_FOLDER: str = r"C:\Games\osu!\Songs"
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
    # check if song is present in any collection
    # return any(song_info.md5_hash in md5s for md5s in collection.collections.values())

    if song_info.gameplay_mode != 3:  # 3 is mania
        return False

    if song_info.circle_size != 7:  # filter out all non-7k
        return False

    if song_info.folder_name.startswith("[_O2Jam_] Xeno"):
        return False

    if song_info.folder_name.startswith("[_O2Jam_] Fantasia"):
        return False

    if song_info.folder_name.startswith("[_O2Jam_] Jupiter"):
        return False

    if song_info.folder_name.startswith("- # IIDX 24 SINOBUZ"):
        return False

    if song_info.folder_name.startswith("[_BMS_]"):
        return False
    
    # return song_info.song_title.startswith("T")
    
    # return song_info.song_title == "Triumphal Return" and song_info.mapper == "Sebaex" and song_info.difficulty == "7K Another"

    return True  # make sure to return True for all other songs


def songs_apply(encoded_song_data: str, song_info: Song.Info):
    """
    this method gets called for every song that got accepted by songs_filter
    song: Song = songdb.decode_to_song(encoded_song_data, song_info)
    to decode it
    """

    # use tqdm.write() instead of print() here qdm.write(song.info.song_title)

    # useless.print_slices_as_beatmap(slices[:10])

    # if "insert collection name here" not in collection.collections:
    #     collection.collections["insert collection name here"] = [] # create empty array if it doesn't exist yet
    # collection.collections["insert collection name here"].append(song.info.md5_hash) # add md5 to collection

    # tqdm.write(f"{song.info.song_title} [{song.info.difficulty}]")

    # 1:36 min without compression
    # 1:33 min with compression ???

    slices: list[Timeslice] = storagedb.select_object("slices", song_info.md5_hash, decompress=True)  # type: ignore
    song = None
    if slices is None:
        song: Song = songdb.decode_to_song(encoded_song_data, song_info)
        slices: list[Timeslice] = Timeslice.generate_timeslices(song)
        storagedb.insert_object("slices", song_info.md5_hash, slices, compress=True)
        
    column_count = song_info.circle_size
    
    score = 0
    
    total_hold_ends = 0
    
    for slice in slices:
        holds = 0
        
        for note in slice.notes:
            if note == Note.HOLD:
                holds += 1
            elif note == Note.HOLD_END:
                total_hold_ends += 1
        
        for note in slice.notes:
            if note == Note.HOLD_END and holds > 0:
                score += 1
                
    if total_hold_ends != song_info.num_sliders:
        print(f"INFO: Slider count mismatch: Got {total_hold_ends}, should be {song_info.num_sliders} for {song_info.md5_hash}: {song_info.artist} - {song_info.song_title} [{song_info.difficulty}]")                

    weight = 0 if total_hold_ends == 0 else score / total_hold_ends
                
                
    key = round(weight, 1)

    if key < 1:
        key = str(key) + " - " + str(round(key + 0.1, 1))
    else:
        key = str(key)

    if key not in collection.collections:
        collection.collections[key] = []
    collection.collections[key].append(song_info.md5_hash)
    
    
    
    return 

    column_count = song_info.circle_size

    if not slices:
        return

    for slice in slices:
        # [Note.NOTE, Note.EMPTY, Note.HOLD, Note.NOTE, Note.EMPTY, Note.NOTE, Note.NOTE] returns {0,3,5,6}
        slice.note_indices = {i for i, x in enumerate(slice.notes) if x == Note.NOTE}
        slice.weighted_count = 1 if len(slice.note_indices) >= 2 else 0
        slice.chordjack_weight = 0

    for index, slice in enumerate(slices[:-1]):  # slices except last element
        next_slice = slices[index + 1]
        intersection = slice.note_indices & next_slice.note_indices  # set intersection -> overlapping notes

        if (
            len(intersection) > 0 and (next_slice.time - slice.time) < 335
        ):  # qualify as chordjack if at least one overlaps
            slice.chordjack_weight = slice.weighted_count

    avg = sum(map(lambda x: x.chordjack_weight, slices)) / len(slices)  # average of all chordjack_weights in slices

    key = round(avg, 1)

    # tqdm.write(f"{key} = {song_info.song_title} [{song_info.difficulty}]")

    if key < 1:
        key = str(key) + " - " + str(round(key + 0.1, 1))
    else:
        key = str(key)

    if key not in collection.collections:
        collection.collections[key] = []
    collection.collections[key].append(song_info.md5_hash)


def on_end() -> None:
    """
    use this to write collections to file
    """
    # collection.write(osu_collection_file) # OVERWRITE(!) collection file
    collection.write("collection.db")


if __name__ == "__main__":
    controller.start()
