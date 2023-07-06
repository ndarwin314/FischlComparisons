from enum import Enum, auto
import numpy as np
from functools import cache

# approx
fourStarMultiplier = 0.746


class DamageType(Enum):
    NORMAL = auto()
    CHARGED = auto()
    PLUNGE = auto()
    SKILL = auto()
    BURST = auto()
    REACTION = auto()
    OTHER = auto()
    # TODO: delete this when i get def ignore
    CLAM = auto()

class Aura(Enum):
    PYRO = auto()
    HYDRO = auto()
    ELECTRO = auto()
    CRYO = auto()
    EC = auto()
    QUICKEN = auto()
    NONE = auto()

class Element(Enum):
    PYRO = auto()
    HYDRO = auto()
    ELECTRO = auto()
    CRYO = auto()
    ANEMO = auto()
    GEO = auto()
    PHYSICAL = auto()
    DENDRO = auto()

    def swirl(self):
        match self:
            case Element.PYRO:
                return Reactions.PYROSWIRL
            case Element.HYDRO:
                return Reactions.HYDROSWIRL
            case Element.ELECTRO:
                return Reactions.ELECTROSWIRL
            case Element.CRYO:
                return Reactions.CRYOSWIRL


class Reactions(Enum):
    PYROSWIRL = auto()
    HYDROSWIRL = auto()
    CRYOSWIRL = auto()
    ELECTROSWIRL = auto()
    OVERLOAD = auto()
    EC = auto()
    SUPERCONDUCT = auto()
    WEAK = auto()
    STRONG = auto()
    AGGRAVATE = auto()
    SPREAD = auto()
    FORWARDVAPE = auto()
    REVERSEVAPE = auto()
    FORWARDMELT = auto()
    REVERSEMELT = auto()
    # no one cares about crystallize
    electro_reactions = {ELECTROSWIRL, OVERLOAD, EC, SUPERCONDUCT}

    def is_swirl(self):
        return self.value < 5

    def is_electro(self):
        return self in electro_reactions

    def element(self):
        match self:
            case Reactions.PYROSWIRL:
                return Element.PYRO
            case Reactions.HYDROSWIRL:
                return Element.HYDRO
            case Reactions.CRYOSWIRL:
                return Element.CRYO
            case Reactions.ELECTROSWIRL:
                return Element.ELECTRO
            case Reactions.OVERLOAD:
                return Element.PYRO
            case Reactions.EC:
                return Element.ELECTRO
            case Reactions.SUPERCONDUCT:
                return Element.CRYO

electro_reactions = {Reactions.ELECTROSWIRL, Reactions.OVERLOAD, Reactions.EC, Reactions.SUPERCONDUCT}

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
    NADMG = 16
    CADMG = 17
    PYRODMG = 18
    HYDRODMG = auto()
    ELECTRODMG = auto()
    CRYODMG = auto()
    ANEMODMG = auto()
    GEODMG = auto()
    PHYSDMG = auto()
    DENDRODMG = auto()
    ECR = auto()
    QCR = auto()
    ECD = auto()
    QCD = auto()
    PLUNGEDMG = auto()
    SWIRLBONUS = auto()
    AGGRAVATEBONUS = auto()
    ELECTROREACTIONBONUS = auto()
    HB = auto()


class ArtifactSlots(Enum):
    FLOWER = 0
    FEATHER = 1
    SANDS = 2
    GOBLET = 3
    CIRCLET = 4


elementDict = {Element.PYRO: Attr.PYRODMG,
               Element.HYDRO: Attr.HYDRODMG,
               Element.ELECTRO: Attr.ELECTRODMG,
               Element.CRYO: Attr.CRYODMG,
               Element.ANEMO: Attr.ANEMODMG,
               Element.GEO: Attr.GEODMG,
               Element.PHYSICAL: Attr.PHYSDMG,
               Element.DENDRO: Attr.DENDRODMG}

class Stats:

    def __init__(self, dict=None):
        self.attributes = np.zeros(35)
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
        return Stats(self.attributes + other.attributes)

    def __sub__(self, other):
        return Stats(self.attributes - other.attributes)

    def __repr__(self):
        return str([(m.name, round(self[m], 3)) for m in list(Attr) if self[m] != 0])

    @cache
    def get_crit_multiplier(self, damageType=None):
        cr = self[Attr.CR]
        cd = self[Attr.CD]
        match damageType:
            case DamageType.SKILL:
                cr += self[Attr.ECR]
                cd += self[Attr.ECD]
            case DamageType.BURST:
                cr += self[Attr.QCR]
                cd += self[Attr.QCD]
            case None:
                pass
        return 1 + cd * max(min(cr, 1), 0)

    @cache
    def get_attack(self):
        return self[Attr.ATKBASE] * (1 + self[Attr.ATKP]) + self[Attr.ATK]

    @cache
    def get_def(self):
        return self[Attr.DEFBASE] * (1 + self[Attr.DEFP]) + self[Attr.DEF]

    @cache
    def get_hp(self):
        return self[Attr.HPBASE] * (1 + self[Attr.HPP]) + self[Attr.HP]

    def get_DMG(self, element=Element.PHYSICAL, damage_type=None, emblem=False):
        base = 1 + self[Attr.DMG] + self[elementDict[element]]
        match damage_type:
            case DamageType.SKILL:
                base += self[Attr.EDMG]
            case DamageType.BURST:
                base += self[Attr.QDMG]
                if emblem:
                    base += self[Attr.ER] / 4
            case DamageType.NORMAL:
                base += self[Attr.NADMG]
            case DamageType.CHARGED:
                base += self[Attr.CADMG]
            case DamageType.PLUNGE:
                base += self[Attr.PLUNGEDMG]
        return base

    def get_multiplier(self, element=Element.PHYSICAL, damage_type=None, emblem=False):
        return self.get_crit_multiplier(damage_type) * self.get_DMG(element, damage_type, emblem)

    # @cache
    def transformative_multiplier(self, reaction: Reactions=None):
        # level = 90
        # levelMultiplier = 0.00194 * level**3-0.319*level*level+30.7*level-868
        emMultiplier = 1 + 16 * self[Attr.EM] / (2000 + self[Attr.EM])
        if reaction is not None and reaction.is_swirl():
            emMultiplier += self[Attr.SWIRLBONUS]
        if reaction is not None and reaction.is_electro():
            emMultiplier += self[Attr.ELECTROREACTIONBONUS]
        return emMultiplier

    def multiplicative_multiplier(self):
        return 1 + 2.78 * self[Attr.EM] / (1400 + self[Attr.EM])
