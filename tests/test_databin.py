from . import TestCase
from src.resources import Resources


class TestDatabin(TestCase):

    def test_server_ids_are_unique(self):
        data_bin = Resources.special("data.bin").content
        monsters = data_bin.monsters
        humans = data_bin.humans
        assert not set(map(lambda x: x.server_id, monsters)).intersection(set(map(lambda x: x.server_id, humans)))
