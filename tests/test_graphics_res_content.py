from . import TestCase
from src.resources import Resources


class TestGraphics(TestCase):

    def test_sprites_are_one_frame(self):
        # show that there is no extra data
        item_sprites = Resources["graphics", "inventory"]
        for hdr in item_sprites:
            assert hdr.record.content.count == 1

        classes = ["ffighter", "fmage", "mfighter", "mmage"]
        for class_ in classes:
            for hdr in Resources["graphics", "equipment", class_]:
                if hdr.record.name in ["primary", "secondary"]:
                    continue
                if len(hdr.record.bytes) == 0:
                    continue
                sprite = hdr.record.content
                assert sprite.count == 1

            for wielding in ["primary", "secondary"]:
                for hdr in Resources["graphics", "equipment", class_, wielding]:
                    if len(hdr.record.bytes) == 0:
                        # skip faulty zero-length images in .RES
                        continue
                    sprite = hdr.record.content
                    assert sprite.count == 1

    def test_count_backpack(self):
        backpack = Resources["graphics", "backpack", "sprites.256"].content
        # this is a sack sprite with 6 various frames for each
        assert len(backpack) == 6
