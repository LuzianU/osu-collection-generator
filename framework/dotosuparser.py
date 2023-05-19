from __future__ import annotations
import hashlib


def read_osu(file: str) -> dict:
    # try:
    with open(file, "rb") as f:
        hash_md5 = hashlib.md5()
        data = f.read()
        hash_md5.update(data)

    # error: bool = False

    osu = data.decode("utf-8", errors="ignore")
    osu = osu.replace("[TimingPoints]", "[TimingPoints]\n")
    osu = osu.replace("[HitObjects]", "[HitObjects]\n")
    osu = osu.splitlines()

    out = {}
    out['md5'] = hash_md5.hexdigest()
    sliders = ['C', 'L', 'P', 'B']

    def blank(line):
        if line == '' or line == '/n':
            return 1

    def get_line(phrase):
        for num, line in enumerate(osu, 0):
            if phrase in line:
                return num

    out['General'] = {}
    out['Metadata'] = {}
    out['Difficulty'] = {}
    out['TimingPoints'] = []
    out['HitObjects'] = []

    general_line = get_line('[General]')
    events_line = get_line('[Events]')
    metadata_line = get_line('[Metadata]')
    difficulty_line = get_line('[Difficulty]')
    events_line = get_line('[Events]')
    timing_line = get_line('[TimingPoints]')
    colour_line = get_line('[Colours]')
    hit_line = get_line('[HitObjects]')

    if not colour_line:
        colour_line = hit_line

    general_list = osu[general_line:metadata_line-1]
    metadata_list = osu[metadata_line:difficulty_line-1]
    difficulty_list = osu[difficulty_line:events_line-1]
    timingpoints_list = osu[timing_line:colour_line-1]
    hitobject_list = osu[hit_line:]

    for item in general_list:
        # try:
        if ':' in item:
            item_ = item.split(': ')
            if (len(item_) > 1):
                out['General'][item_[0]] = item_[1].strip()
            else:
                item_ = item.split(':')
                out['General'][item_[0].strip()] = item_[1].strip()
        # except:
        #    error = True

    for item in metadata_list:
        # try:
        if ':' in item:
            item = item.split(':')
            out['Metadata'][item[0]] = item[1].strip()
        # except:
        #    error = True

    for item in difficulty_list:
        # try:
        if ':' in item:
            item = item.split(':')
            out['Difficulty'][item[0]] = item[1].strip()
        # except:
        #    error = True

    for item in timingpoints_list:
        # try:
        if ',' in item:
            item = item.split(',')
            point = {
                'time': int(float(item[0])),
                'beatLength': float(item[1].strip())
            }
            try:
                point['meter']: int(float(item[2].strip()))
            except:
                'nothing'
            out['TimingPoints'].append(point)
        # except:
        #    error = True

    for item in hitobject_list:
        try:
            if ',' in item:

                item = item.split(',')
                point = {
                    'x': int(float(item[0])),
                    'y': int(float(item[1])),
                    'time': int(float(item[2])),
                    'type': int(float(item[3])),
                    'hitSound': int(float(item[4].strip()))
                }
                if item[5] and sliders not in item:
                    point['extras'] = item[5].strip()
                try:
                    point['slidertype'] = item[6].strip()
                except:
                    'nothing'
                out['HitObjects'].append(point)
        except:
            pass
        #   error = True

    return out  # , error
    # except:
    #    return out, True
