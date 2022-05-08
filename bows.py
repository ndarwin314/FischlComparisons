from attributes import *
from abc import ABC


class Weapon:

    def __init__(self, refinement=1, stats=None, name=""):
        self.stats = Stats() if stats is None else stats
        self.conditionalStats = Stats()
        self.refinement = refinement
        self.name = name

    def get_stats(self):
        return self.stats + self.conditionalStats

    def __repr__(self):
        return f"{self.name} Refinement {self.refinement}"


class PolarStar(Weapon):

    def __init__(self, refinement=1):
        bonus = 0.09 + 0.03*refinement
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.CR: 0.331, Attr.EDMG: bonus, Attr.QDMG: bonus}), "Polar")
        self._polarStacks = 0
        self._stackValue = 0.075 + 0.025 * refinement

    def set_stacks(self, stacks):
        self._polarStacks = stacks
        self.conditionalStats[Attr.ATKP] = stacks * self._stackValue + 0.8 * (1 if stacks == 4 else 0)




class ThunderingPulse(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.CD: 0.662, Attr.ATKP: 0.15 + 0.05 * refinement}), "Pulse")


class AmosBow(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.ATKP: 0.496}), "Amos")

class ElegyForTheEnd(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.ER: 0.551, Attr.EM: 60}), "Elegy")
        self._conditionalActive = False

    def set_passive(self, is_active):
        self._conditionalActive = is_active
        if is_active:
            self.conditionalStats[Attr.ATKP] = 0.15 + 0.05*self.refinement
            self.conditionalStats[Attr.EM] = 75 + 25 * self.refinement



class SkywardHarp(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 674, Attr.CR: 0.221, Attr.CD: 0.15 + 0.05 * refinement}), "Harp")


class Water(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 542, Attr.CD: 0.882, Attr.DMG: 0.15 + 0.05 * refinement,
                                            Attr.HPP: 0.12 + 0.04 * refinement}), "redacted")


class Rust(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.ATKP: 0.461}), "Rust")
        self._conditionalActive = False


class PrototypeCrescent(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.ATKP: 0.461}), "Crescent")
        self._conditionalActive = False

    def set_passive(self, is_active):
        self._conditionalActive = is_active
        self.conditionalStats[Attr.ATKP] = (0.27 + 0.09 * self.refinement) * is_active


class TheViridescentHunt(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.CR: 0.276}), "Hunt")


class AlleyHunter(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 565, Attr.ATKP: 0.276}), "Alley")
        self._stacks = False
        self._stackValue = 0.015 + 0.005 * refinement

    def set_stacks(self, stacks):
        self._stacks = stacks
        self.conditionalStats[Attr.DMG] = stacks * self._stackValue


class TheStringless(Weapon):
    def __init__(self, refinement=1):
        temp = 0.18 + 0.06 * refinement
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.EM: 165, Attr.EDMG: temp, Attr.QDMG: temp}), "Stringless")

class MouunsMoon(Weapon):
    def __init__(self, refinement=1):
        temp = 280 * (0.0009 + 0.0003 * refinement)
        super().__init__(refinement, Stats({Attr.ATKBASE: 565, Attr.ATKP: 0.276, Attr.QDMG: temp}), "Moon Moon")

class WindblumeOde(Weapon):
    def __init__(self, refinement=5):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.EM: 165, Attr.ATKP: 0.32}), "Ode")
        self.skill_activated = False

    def skill_cast(self, var):
        self.skill_activated = var
        self.conditionalStats[Attr.ATKP] = 0.32 if var else 0

class SacrificialBow(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 565, Attr.ER: 0.306}), "Sac")

class FavoniusWarbow(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 454, Attr.ER: 0.613}), "Fav")

class Hamayumi(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 454, Attr.ATKP: 0.551}), "Hamayumi")

class MitternachtsWaltz(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510}), "Waltz")
        self.passive_active = False

    def set_passive(self, value):
        self.passive_active = value
        self.conditionalStats[Attr.EDMG] = (0.15 + 0.05 * self.refinement) * value
