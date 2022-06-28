import math
from attributes import *
import buff as b
from abc import ABC
from actions import OtherAction, Buff
from uuid import uuid1 as uuid
import buff


class Weapon:

    def __init__(self, refinement=1, stats=None, name=""):
        self.stats = Stats() if stats is None else stats
        self.conditionalStats = Stats()
        self.refinement = refinement
        self.name = name
        self.proc_chance = 0
        self.proc_scaling = 0

    def get_stats(self, rotation):
        return self.stats + self.conditionalStats

    def __repr__(self):
        return f"{self.name} Refinement {self.refinement}"

    def damage_proc(self, stats, chances=1):
        return self.proc_scaling * stats.get_attack() * stats.get_crit_multiplier() * \
               (1 + stats[Attr.PHYSDMG] + stats[Attr.DMG]) * (1 - (1 - self.proc_chance) ** chances)

    def equip(self, character):
        character.weapon = self


class PolarStar(Weapon):

    def __init__(self, refinement=1):
        bonus = 0.09 + 0.03 * refinement
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.CR: 0.331, Attr.EDMG: bonus, Attr.QDMG: bonus}),
                         "Polar")
        self._polarStacks = 0
        stack = 0.075 + 0.025 * refinement
        self.stackValue = [i * stack for i in range(5)]
        self.stackValue[4] += stack * 0.8
        self.stacks = {"normal": None, "charged": None, "skill": None, "burst": None}

    """def set_stacks(self, stacks):
        self._polarStacks = stacks
        self.conditionalStats[Attr.ATKP] = stacks * self.stack + 0.8 * (1 if stacks == 4 else 0)"""

    def stack(self, rot, key):
        self.stacks[key] = rot.time + 12

    def get_stats(self, time):
        stackCount = 0
        for k in self.stacks:
            expiration = self.stacks[k]
            if expiration is None:
                continue
            elif expiration < time:
                self.stacks[k] = None
            else:
                stackCount += 1
        return self.stats + Stats({Attr.ATKP: self.stackValue[stackCount]})

    def equip(self, character):
        super().equip(character)
        character.normalHitHook.append(lambda t: self.stack(t, "normal"))
        character.chargedHitHook.append(lambda t: self.stack(t, "charged"))
        character.skillHitHook.append(lambda t: self.stack(t, "skill"))
        character.burstHitHook.append(lambda t: self.stack(t, "burst"))


class ThunderingPulse(Weapon):
    def __init__(self, refinement=1):
        # do something for stacks, currently assuming flat 2
        super().__init__(refinement,
                         Stats({Attr.ATKBASE: 608, Attr.CD: 0.662, Attr.ATKP: 0.15 + 0.05 * refinement}),
                         "Pulse")
        # assume
        self.stackValue = [0, 0.09 + 0.03 * refinement, 0.18 + 0.06 * refinement, 0.3 + 0.1 * refinement]
        self.stacks = {"normal": None, "skill": None, "energy": math.inf}

    def normal_hit(self, rot):
        self.stacks["normal"] = rot.time + 5

    def skill_cast(self, rot):
        self.stacks["normal"] = rot.time + 10

    def get_stats(self, time):
        stackCount = 0
        for k in self.stacks:
            expiration = self.stacks[k]
            if expiration is None:
                continue
            elif expiration < time:
                self.stacks[k] = None
            else:
                stackCount += 1
        return self.stats + Stats({Attr.NADMG: self.stackValue[stackCount]})

    def equip(self, character):
        super().equip(character)
        character.skillCastHook.append(lambda c: OtherAction(character, c.time, lambda r: c.weapon.skill_cast(r)))
        character.normalHitHook.append(self.normal_hit)


class AmosBow(Weapon):

    def __init__(self, refinement=1):
        buff = 0.09 + 0.03 * refinement
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.ATKP: 0.496, Attr.NADMG: buff, Attr.CADMG: buff}),
                         "Amos")


class ElegyForTheEnd(Weapon):
    buffID = uuid()

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 608, Attr.ER: 0.551, Attr.EM: 60}), "Elegy")
        self.sigils = 0
        self.lastHit = -1
        self.buff = Stats({Attr.EM: 75 + 25 * self.refinement, Attr.ATKP: 0.15 + 0.05 * self.refinement})

    def skill_burst_hit(self, char):
        t = char.time
        if t > self.lastHit + 0.2:
            self.sigils += 1
            self.lastHit = t
        if self.sigils == 4:
            self.sigils = 0
            self.lastHit += 20
            char.rotation.add_event(Buff(None, t, buff.Buff(self.buff, t, 12, self.buffID)))

    def equip(self, character):
        super().equip(character)
        character.skillHitHook.append(self.skill_burst_hit)
        character.burstHitHook.append(self.skill_burst_hit)


class SkywardHarp(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 674, Attr.CR: 0.221, Attr.CD: 0.15 + 0.05 * refinement}),
                         "Harp")
        self.proc_chance = 0.5 + 0.1 * refinement
        self.proc_scaling = 1.25


class Water(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 542, Attr.CD: 0.882, Attr.DMG: 0.15 + 0.05 * refinement,
                                            Attr.HPP: 0.12 + 0.04 * refinement}), "Aqua")


class Rust(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.ATKP: 0.461,
                                            Attr.NADMG: 0.3 * 0.1 * refinement, Attr.CADMG: -0.1}), "Rust")


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
        self.proc_chance = 0.5
        self.proc_scaling = (0.4 + 0.1 * refinement) * 8


class AlleyHunter(Weapon):

    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 565, Attr.ATKP: 0.276, Attr.DMG: 0.15 + 0.05 * refinement}),
                         "Alley")
        self._stacks = False
        self._stackValue = 0.015 + 0.005 * refinement

    def set_stacks(self, stacks):
        self._stacks = stacks
        self.conditionalStats[Attr.DMG] = stacks * self._stackValue


class TheStringless(Weapon):
    def __init__(self, refinement=1):
        temp = 0.18 + 0.06 * refinement
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.EM: 165, Attr.EDMG: temp, Attr.QDMG: temp}),
                         "Stringless")


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
        super().__init__(refinement, Stats({Attr.ATKBASE: 454, Attr.ATKP: 0.551,
                                            Attr.NADMG: 0.12 * refinement * 5, Attr.CADMG: 0.09 + 0.03 * refinement}),
                         "Hamayumi")


class MitternachtsWaltz(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.PHYSDMG: 0.517}), "Waltz")
        self.passive_active = False

    def set_passive(self, value):
        self.passive_active = value
        self.conditionalStats[Attr.EDMG] = (0.15 + 0.05 * self.refinement) * value


class Twilight(Weapon):
    def __init__(self, refinement=1):
        # assuming constant middle state cause idgaf
        super().__init__(refinement, Stats({Attr.ATKBASE: 565, Attr.ER: 0.306, Attr.DMG: 0.075 + 0.025 * refinement}),
                         "Twilight")


class AlleyFlash(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 620, Attr.EM: 55, Attr.DMG: 0.09 + 0.03 * refinement}),
                         "Alley Flash")


class IronSting(Weapon):

    def __init__(self, refinement=5):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.EM: 165, Attr.DMG: 0.09 + 0.03 * refinement}),
                         "Iron Sting")

    def equip(self, character):
        super().equip(character)
        # character

    def on_damage(self, rotaation):
        pass


class Catch(Weapon):
    def __init__(self, refinement=5):
        super().__init__(refinement, Stats({Attr.ATKBASE: 510, Attr.ER: 0.459, Attr.QDMG: 0.32, Attr.QCR: 0.12}),
                         '"The Catch"')


class Grass(Weapon):
    def __init__(self, refinement=1):
        super().__init__(refinement, Stats({Attr.ATKBASE: 608}), "Engulfing Lightning")
