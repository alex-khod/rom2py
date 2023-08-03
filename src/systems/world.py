from src.mobj import Objects, MapUnits, Structures


class World:
    objects = None
    units = None

    @classmethod
    def from_alm2(self, alm2):
        self.objects = Objects()
        self.units = MapUnits()