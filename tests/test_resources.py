from src import resources
from src.resources import Resources
from tests import TestCase


class TestResourceLookup(TestCase):

    def test_res_lookup(self):
        assert isinstance(Resources["graphics"], resources.Resource)
        assert isinstance(Resources["world"], resources.Resource)

    def test_deep_res_lookup(self):
        """ Make sure correct resources are found, identified by their size."""
        bytes_arr = Resources["graphics", "objects", "iva1", "dead", "sprites.256"].bytes
        assert len(bytes_arr) == 1184

        bytes_arr = Resources["graphics", "objects", "iva1", "sprites.256"].bytes
        assert len(bytes_arr) == 10149

        bytes_arr = Resources["graphics", "objects", "bambuk1", "dead", "sprites.256"].bytes
        assert len(bytes_arr) == 2015

        bytes_arr = Resources["graphics", "objects", "bambuk1", "sprites.256"].bytes
        assert len(bytes_arr) == 2385

    def test_resource_is_cached(self):
        res = Resources["graphics"]
        assert id(res) == id(Resources["graphics"])

    def test_special_lookup(self):
        assert isinstance(Resources.special("units.reg"), resources.ResourceRecordFile)

    def test_res_directory_lookup(self):
        assert type(Resources["graphics", "units"]) is list
        assert type(Resources[("graphics", "units")]) is list
        assert type(Resources["graphics"]["units"]) is list

    def test_res_file_lookup(self):
        assert isinstance(Resources["graphics", "units", "units.reg"], resources.ResourceRecordFile)
