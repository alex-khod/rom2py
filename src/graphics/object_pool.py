class ObjectPool:
    def __init__(self, object_class):
        self._class = object_class
        self._counter = 0
        self._objects = []
        self._free = []
        self._consumed = []

    def acquire(self):
        if self._free:
            object = self._free.pop()
            self._consumed.append(object)
            return object
        else:
            object = self._class()
            self._consumed.append(object)
            return object

        # if self._free:
        #     key = self._free.pop()
        #     object = self._objects[key]
        #     self._consumed.add(key)
        #     return object
        # else:
        #     object = self._class()
        #     key = self._counter
        #     self._counter += 1
        #     self._consumed.add(key)
        #     return object

    def free(self, object):
        self._consumed.remove(object)
        self._free.append(object)
