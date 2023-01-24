class np:
    # Numpy mock to test running with PyPy.

    @staticmethod
    def array(array, dtype="uint8"):
        return array

    @staticmethod
    def zeros(shape, dtype="uint8", value=0):
        if len(shape) == 2:
            h, w = shape
            return [[value] * w for _ in range(h)]
        elif len(shape) == 3:
            h, w, c = shape
            return [[[value] * c for _ in range(w)] for _ in range(h)]
        raise NotImplemented