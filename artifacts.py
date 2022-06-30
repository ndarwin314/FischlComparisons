from enum import Enum

class Set(Enum):
    TF = 0
    ATK = 1
    TS = 2
    GAMBLER = 3
    NO = 4
    TOM = 5
    EMBLEM = 6
    VV = 7

    def __repr__(self):
        return self.name

# represents a pair of an artifact set with its count, ie 4 piece emblem
class SetCount:

    __slots__ = ["set", "count"]

    def __init__(self, set, count):
        self.set = set
        self.count = count

    def __repr__(self):
        return f"{self.count} {self.set}"
