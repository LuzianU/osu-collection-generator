from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import unicodedata
import buffer_io as buffer_io


class Collection:
    def __init__(self) -> None:
        self.version: int = int(datetime.today().strftime('%Y%m%d'))
        self.collections: dict[str, list[str]] = {}

    def read(self, file: str) -> None:
        """import from a collection.db file"""
        with open(file, "rb") as f:
            self.version = buffer_io.read_uint(f)
            num_collections = buffer_io.read_uint(f)
            for _ in range(num_collections):
                name = buffer_io.read_string(f)
                size = buffer_io.read_uint(f)
                self.collections[name] = []
                for _ in range(size):
                    self.collections[name].append(buffer_io.read_string(f))

    def write(self, file: str) -> None:
        """exports self to a collection.db file"""
        with open(file, "wb") as f:
            buffer_io.write_uint(f, self.version)
            buffer_io.write_uint(f, len(self.collections))
            for name, md5s in self.collections.items():
                buffer_io.write_string(f, str(name))
                buffer_io.write_uint(f, len(md5s))
                for md5 in md5s:
                    buffer_io.write_string(f, str(md5))


@dataclass
class Song:
    """Describes a playable osu! song
        info: information about the song which is stored in the osu!.db file
        dict: dict containing parsed .osu file lines.
            see: https://osu.ppy.sh/wiki/en/Client/File_formats/Osu_%28file_format%29"""
    @dataclass
    class Info:
        """Describes song information of the osu!.db file
            see: https://github.com/ppy/osu/wiki/Legacy-database-file-structure"""
        artist: str
        artist_unicode: str
        song_title: str
        song_title_unicode: str
        mapper: str
        difficulty: str
        audio_file: str
        md5_hash: str
        map_file: str
        ranked_status: int
        num_hitcircles: int
        num_sliders: int
        num_spinners: int
        last_modified: int
        approach_rate: float
        circle_size: float
        hp_drain: float
        overall_difficulty: float
        slider_velocity: float
        drain_time: int
        total_time: int
        preview_time: int
        beatmap_id: int
        beatmap_set_id: int
        thread_id: int
        grade_standard: int
        grade_taiko: int
        grade_ctb: int
        grade_mania: int
        local_offset: int
        stack_leniency: float
        gameplay_mode: int
        song_source: str
        song_tags: str
        online_offset: int
        title_font: str
        is_unplayed: int
        last_played: int
        is_osz2: int
        folder_name: str
        last_checked: int
        ignore_sounds: int
        ignore_skin: int
        disable_storyboard: int
        disable_video: int
        visual_override: int
        last_modified2: int
        scroll_speed: int
        star_ratng_osu: float
        star_rating_taiko: float
        star_ratiing_ctb: float
        star_rating_mania: float

    info: Info
    dict: dict
