from enum import Enum, auto
from abc import ABC
from attributes import Attr, Stats, DamageType, Element
import actions
import buff
from uuid import uuid4 as uuid

class Set(Enum):
    TF = 0
    ATK = 1
    TS = 2
    GAMBLER = 3
    NO = 4
    TOM = 5
    EMBLEM = 6
    VV = 7
    OHC = 8
    SHIME = auto()
    INSTRUCTOR = auto()
    GD = auto()

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

class SetBase(ABC):
    __slots__ = ["count"]
    def __init__(self, count):
        self.count = count

    def two(self, character: "character.Character"):
        pass

    def four(self, character: "character.Character"):
        pass

    def add(self, char: "character.Character"):
        # add some type checking but i think there is circular import bs
        if self.count >= 2:
            self.two(char)
            if self.count >= 4:
                self.four(char)


class Glad(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.ATKP] += 0.18
        
class Shime(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.ATKP] += 0.18
        
    def four(self, character: "character.Character"):
        def shime(char: "character.Character"):
            character.rotation.add_event(
                actions.Buff(char,
                             char.time,
                             buff.Buff(
                                 Stats({Attr.NADMG: 0.5, Attr.CADMG: 0.5, Attr.PLUNGEDMG: 0.5}),
                                 char.time,
                                 10,
                                 "character.Character".shimeID
                             ),
                             on_field=True))

        character.skillCastHook.append(shime)
        
class TF(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.ELECTRODMG] += 0.15
        
    def four(self, character: "character.Character"):
        character.artifactStats[Attr.AGGRAVATEBONUS] += 0.2
        # TODO: add other bonuses


class TS(SetBase):

    def four(self, character: "character.Character"):
        character.artifactStats[Attr.DMG] += 0.35
        # TODO: probably a better way to do this now

class Gambler(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.EDMG] += 0.2

class NO(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.QDMG] += 0.2

    def four(self, character: "character.Character"):
        delegate = lambda c: actions.Buff(self, c.time,
                                         buff.Buff(character.noblesseBuff, c.time, 12, character.noblesseID))
        character.burstCastHook.append(delegate)

class TOM(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.HPP] += 0.2

    def four(self, character: "character.Character"):
        """delegate = lambda c: actions.Buff(self, c.time, Buff(self.noblesseBuff, c.time, 3, self.tomID))"""
        def tom(char: "character.Character"):
            t = char.time + 0.1
            if t > char.lastTOM + 0.5:
                char.rotation.add_event(
                    actions.Buff(character, t, buff.Buff(character.noblesseBuff, t, 3, character.tomID)))

        character.skillHitHook.append(tom)

class Emblem(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.ER] += 0.2

    def four(self, character: "character.Character"):
        character.emblem = True

class VV(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.ANEMODMG] += 0.15

    def four(self, character: "character.Character"):
        character.vv = True
        character.artifactStats[Attr.SWIRLBONUS] += 0.6

class OHC(SetBase):
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.HB] += 0.15

    def four(self, character: "character.Character"):
        def ohc(char, healing):
            t = char.time
            if t <= 3 + self.lastOHC:
                character.OHCMV.flat = min(character.OHCMV.flat + 0.9 * healing, 27_000)
            elif t <= 3.5:
                pass
            else:  # t > 3.5
                character.OHCMV.flat = 0
                char.do_damage(character.OHCMV, Element.PHYSICAL, DamageType.CLAM, t + 3)
                self.lastOHC = t

        character.healingHook.append(ohc)

class Instructor(SetBase):
    id = uuid()
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.EM] += 80

    def four(self, character: "character.Character"):
        def instructor(char: "character.Character", reaction):
            character.rotation.add_event(
                actions.Buff(char,
                             char.time,
                             buff.Buff(
                                 Stats({Attr.EM: 120}),
                                 char.time,
                                 8,
                                 Instructor.id
                             )))

        character.reactionHook.append(instructor)

class Gilded(SetBase):
    id = uuid()
    def two(self, character: "character.Character"):
        character.artifactStats[Attr.EM] += 80

    def four(self, character: "character.Character"):
        def gd(char: "character.Character", reaction):
            char.add_buff(buff.Buff(Stats({Attr.ATKP: 0.14, Attr.EM: 100}), char.time, 8, Gilded.id))
            # TODO: check this works and make dynamic
            character.reactionHook.append(gd)







