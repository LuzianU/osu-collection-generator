# https://raw.githubusercontent.com/jaasonw/osu-db-tools/master/buffer.py
from __future__ import annotations
from io import BufferedReader, BufferedWriter
import struct

struct_bool = struct.Struct("<?")
struct_ubyte = struct.Struct("<B")
struct_ushort = struct.Struct("<H")
struct_uint = struct.Struct("<I")
struct_float = struct.Struct("<f")
struct_double = struct.Struct("<d")
struct_ulong = struct.Struct("<Q")


def read_bool(buffer: BufferedReader) -> bool:
    return struct_bool.unpack(buffer.read(1))[0]


def read_ubyte(buffer: BufferedReader) -> int:
    return struct_ubyte.unpack(buffer.read(1))[0]


def read_ushort(buffer: BufferedReader) -> int:
    return struct_ushort.unpack(buffer.read(2))[0]


def read_uint(buffer: BufferedReader) -> int:
    return struct_uint.unpack(buffer.read(4))[0]


def read_float(buffer: BufferedReader) -> float:
    return struct_float.unpack(buffer.read(4))[0]


def read_double(buffer: BufferedReader) -> float:
    return struct_double.unpack(buffer.read(8))[0]


def read_ulong(buffer: BufferedReader) -> int:
    return struct_ulong.unpack(buffer.read(8))[0]


def read_int_double(buffer: BufferedReader) -> "tuple[int, float]":
    # read_ubyte(buffer)
    buffer.seek(1, 1)
    integer = read_uint(buffer)
    buffer.seek(1, 1)
    # read_ubyte(buffer)
    double = read_double(buffer)
    return (integer, double)


def read_timing_point(buffer: BufferedReader) -> "tuple[float, float, bool]":
    bpm = read_double(buffer)
    offset = read_double(buffer)
    inherited = read_bool(buffer)
    return (bpm, offset, inherited)


def read_string(buffer: BufferedReader) -> str:
    strlen = 0
    strflag = read_ubyte(buffer)
    if (strflag == 0x0b):
        strlen = 0
        shift = 0
        # uleb128
        # https://en.wikipedia.org/wiki/LEB128
        while True:
            byte = read_ubyte(buffer)
            strlen |= ((byte & 0x7F) << shift)
            if (byte & (1 << 7)) == 0:
                break
            shift += 7

    return buffer.read(strlen).decode("utf-8")


def write_ubyte(f: BufferedWriter, data: int):
    f.write(struct.pack("<B", data))


def write_uint(f: BufferedWriter, data: int):
    f.write(struct.pack("<I", data))


def write_string(f: BufferedWriter, data: str):
    if len(data) > 0:
        write_ubyte(f, 0x0b)
        strlen = b""
        value = len(data.encode('utf-8'))
        while value != 0:
            byte = (value & 0x7F)
            value >>= 7
            if value != 0:
                byte |= 0x80
            strlen += struct.pack("<B", byte)
        f.write(strlen)
        f.write(struct.pack("<" + str(len(data.encode("utf-8"))) +
                            "s", data.encode("utf-8")))
    else:
        write_ubyte(f, 0x0)
