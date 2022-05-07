from enum import Enum
import numpy as np

class Attr(Enum):
    HPP = 0
    HP = 1
    ATKP = 2
    ATK = 3
    DEFP = 4
    DEF = 5
    EM = 6
    ER = 7
    CR = 8
    CD = 9
    HPBASE = 10
    ATKBASE = 11
    DEFBASE = 12
    DMG = 13
    EDMG = 14
    QDMG = 15
    ELEMENTDMG = 16

class Stats:

    def __init__(self, dict=None):
        self.attributes = np.zeros(17)
        if isinstance(dict, np.ndarray):
            self.attributes = dict
            return
        elif dict is None:
            return
        for k, v in dict.items():
            self.attributes[k.value] = v

    def __getitem__(self, item):
        return self.attributes[item.value]

    def __setitem__(self, item, value):
        self.attributes[item.value] = value

    def __add__(self, other):
        return Stats(self.attributes+other.attributes)

    def __repr__(self):
        return str([(m.name, round(self[m], 3)) for m in list(Attr)])

    def get_crit_multiplier(self):
        return 1 + self[Attr.CD]*min(self[Attr.CR], 1)

    def get_attack(self):
        return self[Attr.ATKBASE] * (1 + self[Attr.ATKP]) + self[Attr.ATK]

    def transformative_multiplier(self):
        level = 90
        levelMultiplier = 0.00194 * level**3-0.319*level*level+30.7*level-868
        emMultiplier = 1 + 16 * self[Attr.EM] / (2000 + self[Attr.EM])
        return levelMultiplier * emMultiplier