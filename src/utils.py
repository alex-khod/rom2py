import os

def memusage():
    import os, psutil
    return psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)

def dumpobj(obj):
    """
        Print object non-magic properties and methods.
    """
    attr_list = dir(obj)
    methods = []
    for k in attr_list:
        if k[0] != "_":
            v = getattr(obj, k)
            if callable(v):
                methods.append((k, v))
            else:
                print(k, v)
    if methods:
        print("\nMethods")
    for k, v in methods:
        print(k, v)

# todo test

def split_path(path):
    """
        Split path by separator and reverse it.
        "foo/bar/kek" -> ["kek", "bar", "foo"]
    """

    parts = []
    while path:
        path, part = os.path.split(path)
        parts.append(part)
    return parts[::-1]


# todo test

def natural_sort(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


class VertexAllocator:
    """
        Simplest hack to index vertexes.
        That is, accept a vertex list and return indexes,
        increasing vertex idx only if alloc() vertex is not in verts_dict.
    """

    def __init__(self):
        self.idx = 0
        self.verts_dict = {}

    def alloc(self, vert_quads, tex_quads=None):
        idxs = []
        verts = []
        tex_cs = []
        n = len(vert_quads) // 2
        if tex_quads is None:
            tex_quads = (0, 0, 0) * n
        tex_quads = tuple(tex_quads)
        vert_quads = tuple(vert_quads)
        for k in range(0, n):
            x, y = v = vert_quads[k * 2:k * 2 + 2]
            if v in self.verts_dict:
                idxs.append(self.verts_dict[v])
            else:
                # print(x, y, 'out')
                verts += [x, y]
                idxs.append(self.idx)
                # tex_cs += tex_quads[k * 2:k * 2 + 2]
                tex_cs += tex_quads[k * 3:k * 3 + 3]
                self.verts_dict[v] = self.idx
                self.idx += 1

        return tuple(verts), tuple(idxs), tuple(tex_cs)


from dataclasses import dataclass


@dataclass
class Box:
    """
        Just a barebones rectangle.
    """

    x: float
    y: float
    w: float
    h: float

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y + self.h

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y


def has_intersection(box1: Box, box2: Box):
    return box2.left < box1.right and box2.right > box1.left and box2.top > box1.bottom and box2.bottom < box1.top


def get_intersection(box1: Box, box2: Box):
    if not has_intersection(box1, box2):
        return None
    left = max(box1.left, box2.left)
    bottom = max(box1.bottom, box2.bottom)
    right = min(box1.right, box2.right)
    top = min(box1.top, box2.top)
    return left, bottom, right, top
