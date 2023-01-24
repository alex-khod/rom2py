from . import TestCase


class DummyA:
    class_thing = 25
    thing = None

    def __init__(self, thing):
        self.thing = thing

    def thing_through_call(self):
        return self.thing

    def class_thing_through_call(self):
        return self.class_thing


class DummyB:
    __slots__ = "a", "b", "thing"
    class_thing = 25

    def __init__(self, thing):
        self.thing = thing


class TestFilterDummyA(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.list = [DummyA(75) for i in range(500_000)] + [DummyA(25) for i in range(500_000)]

    def test_filter_thing(self):
        return list(filter(lambda x: x.thing > 25, self.list))

    def test_filter_class_thing(self):
        return list(filter(lambda x: x.class_thing > 25, self.list))

    def test_filter_thing_through_call(self):
        return list(filter(lambda x: x.thing_through_call() > 25, self.list))

    def test_filter_class_thing_through_call(self):
        return list(filter(lambda x: x.class_thing_through_call() > 25, self.list))


class TestFilterDummyB(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.list = [DummyB(75) for i in range(500_000)] + [DummyB(25) for i in range(500_000)]

    def test_filter_thing(self):
        return list(filter(lambda x: x.thing > 25, self.list))

    def test_filter_class_thing(self):
        return list(filter(lambda x: x.class_thing > 25, self.list))


class TestFilterMultipleLoops(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.list = [DummyB(75) for i in range(5000)] + [DummyB(25) for i in range(5000)]

    def test_filter_multiple_loops(self):
        result = [None] * 100
        for i in range(len(result)):
            result = list(filter(lambda x: x.thing > 25, self.list))
        return result
