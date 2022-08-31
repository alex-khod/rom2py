from src.utils import Vec2


class Layer:
    def __init__(self, w, h):
        self._items = [[None for _ in range(w)] for _ in range(h)]

    def __getitem__(self, item: Vec2):
        return self._items[item.y][item.x]

    def __setitem__(self, item: Vec2, value):
        self._items[item.y][item.x] = value
