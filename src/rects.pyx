cdef class Rect:
    cdef public int left
    cdef public int top
    cdef public int right
    cdef public int bottom

    def __init__(self, int left, int top, int right, int bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __repr__(self):
        return "Rect l%d t%d r%d b%d" % (self.left, self.top, self.right, self.bottom)

# ctypedef struct Rect:
#     int left
#     int right
#     int width
#     int height

cdef inline int has_intersect(Rect rect1, Rect rect2):
    return rect2.left < rect1.right and rect2.right > rect2.left and rect2.top < rect1.bottom and rect2.bottom > rect1.top

# cdef vector[Rect] _filter_rects(Rect rect, vector[Rect] rects):
#     return [x for x in rects if has_intersect(rect, x)]

# def filter_rects(rect, rects):
#     return list(_filter_rects(rect, rects))

def filter_rects_by_intersect(rect : Rect, rects : list[object]):
    return [x for x in rects if has_intersect(rect, x.rect) > 0]