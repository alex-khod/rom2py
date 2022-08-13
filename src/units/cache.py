import struct
import numpy as np
from src.resources import Resources, get_resource_at_root

def load_units():
    unit_registry = Resources.special("units.reg").content
    units = unit_registry.units_by_id

    framedict = {}
    for u in units.values():
        filename = u["filename"]
        u256 = Resources["graphics", "units", filename + '.256'].content
        try:
            framedict[filename] = [img.to_colors() for img in u256]
        except AssertionError:
            print(f"{filename} is invalid: value 0 in color space.")
    return framedict

def save_units_cache(framedict):
    
    def write_integer(f, x):
        f.write(struct.pack(">L", x))

    path = get_resource_at_root("data",  "256cache.bin")
    with open(path, "wb") as f:
        write_integer(f, 0xdeadc0de)
        for file, frames in framedict.items():
            fname_bytes = bytes(file, "utf-8")
            fname_len = len(fname_bytes)
            write_integer(f, fname_len)
            f.write(fname_bytes)
            frame_count = len(frames)
            write_integer(f, frame_count)
            for fr in frames:
                frame_bytes = fr.tobytes()
                frame_len = len(frame_bytes)
                write_integer(f, frame_len)
                write_integer(f, fr.shape[1])
                write_integer(f, fr.shape[0])
                f.write(frame_bytes)

def load_units_cache():

    def read_integer(f):
        return struct.unpack(">L", f.read(4))[0]

    framedict = {}
    path = get_resource_at_root("data", "256cache.bin")
    with open(path, "rb") as f:
        assert read_integer(f) == 0xdeadc0de
        while True:
            len_bytes = f.read(4)
            if not len_bytes:
                break
            HERE = 1
            f.seek(-4, HERE)
            fname_len = read_integer(f)
            fname = f.read(fname_len).decode("utf-8")
            frame_count = read_integer(f)
            frames = []
            for i in range(frame_count):
                frame_len = read_integer(f)
                w = read_integer(f)
                h = read_integer(f)
                frame_bytes = f.read(frame_len)
                frame = np.frombuffer(frame_bytes, count=frame_len, dtype='uint8')
                frame = frame.reshape((h, w))
                frames.append(frame)
            framedict[fname] = frames
    return framedict

class UnitsCache:
    _cache = None

    def __new__(cls):
        if cls._cache is None:
            try:
                cls._cache = load_units_cache()
            except FileNotFoundError:
                print("No cache, creating...")
                framedict = load_units()
                cls._cache = framedict
                save_units_cache(framedict)
        return cls._cache