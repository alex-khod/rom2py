from src.resources import Resources
from src.formats.sprites.base import ROM256 as ROM256Python
from src.formats.sprites.base import ROM16A as ROM16APython


def write_test_data():
    import os
    _bytes = Resources["graphics", "objects", "bambuk1", "sprites.256"].bytes
    rom256 = ROM256Python.from_bytes(_bytes)
    idxs = rom256[0].to_color_indexes()
    with open(os.path.join("data", "bambuk.bin"), "wb") as f:
        _bytes = idxs.tobytes()
        f.write(_bytes)

    _bytes = Resources["graphics", "interface", "inn", "unit1", "sprites.16a"].bytes
    # from src.formats.sprites.base import ROM16A as A16Python
    rom16a = ROM16APython.from_bytes(_bytes)
    idxs = rom16a[0].to_color_indexes()
    import os
    with open(os.path.join("data", "unit.bin"), "wb") as f:
        _bytes = idxs.tobytes()
        f.write(_bytes)


if __name__ == "__main__":
    write_test_data()
    print("Done")
