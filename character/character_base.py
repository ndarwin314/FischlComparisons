from attributes import Element, Reactions, Attr, Stats, DamageType
from enemy import ResShred
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid1 as uuid
from summon import Summon
import math
import numpy as np
import actions
from artifacts import Set, SetCount
import buff
import mv

class ConType(Enum):
    SkillFirst = 0
    BurstFirst = 0


"""mainStats = {ArtifactSlots.FLOWER: Attr.HP,
             ArtifactSlots.FEATHER: Attr.ATK,
             ArtifactSlots.SANDS: Attr.ATKP,
             ArtifactSlots.GOBLET: Attr.ELEMENTDMG}"""
"""mainStatValues = {ArtifactSlots.FLOWER: 4780,
                  ArtifactSlots.FEATHER: 311,
                  ArtifactSlots.SANDS: 0.466,
                  ArtifactSlots.GOBLET: 0.466,
                  ArtifactSlots.CIRCLET: 0.311}"""

elementDict = {Element.PYRO: Attr.PYRODMG,
               Element.HYDRO: Attr.HYDRODMG,
               Element.ELECTRO: Attr.ELECTRODMG,
               Element.CRYO: Attr.CRYODMG,
               Element.ANEMO: Attr.ANEMODMG,
               Element.GEO: Attr.GEODMG,
               Element.PHYSICAL: Attr.PHYSDMG}
scalingMultiplier = [0,
                     1,
                     1.075,
                     1.15,
                     1.25,
                     1.325,
                     1.4,
                     1.5,
                     1.6,
                     1.7,
                     1.8,
                     1.9,
                     2,
                     2.125]

physHighMultiplier = [0,
                      1,
                      1.068,
                      1.136,
                      1.227,
                      1.295,
                      1.375,
                      1.477,
                      1.58,
                      1.682,
                      1.784,
                      1.886,
                      1.989,
                      2.091,
                      2.193,
                      2.295]

autoMultiplier = [0,
                  1,
                  1.081,
                  1.163,
                  1.279,
                  1.36,
                  1.453,
                  1.581,
                  1.709,
                  1.837,
                  1.977,
                  2.116,
                  2.256,
                  2.395,
                  2.535,
                  2.674]

physhighMultiplier = [0,
                      1,
                      1.081,
                      1.163,
                      1.279,
                      1.36,
                      1.453,
                      1.581,
                      1.709,
                      1.837,
                      1.977,
                      2.137,
                      2.325,
                      2.513,
                      2.701,
                      2.906]
substatValues = {Attr.HPP: 0.0496, Attr.HP: 253.94,
                 Attr.ATKP: 0.0496, Attr.ATK: 16.54,
                 Attr.DEFP: 0.0620, Attr.DEF: 19.68,
                 Attr.EM: 19.82, Attr.ER: 0.051,
                 Attr.CR: 0.0331, Attr.CD: 0.0662}


class Character(ABC):
    noblesseID = uuid()
    noblesseBuff = Stats({Attr.ATKP: 0.2})
    vvID = uuid()
    tomID = uuid()

    def __init__(self, stats, element, auto_talent, skill_talent, burst_talent,
                 constellation, weapon, artifact_set, weapon_type, energy_cost):
        self.rotation = None

        # hooks
        self.burstCastHook = []
        self.burstHitHook = []
        self.skillCastHook = []
        self.skillHitHook = []
        self.normalHitHook = []
        self.chargedHitHook = []
        self.damageHook = []


        self.stats = stats
        self.buffs = []
        self.artifactStats = Stats()
        self.element = element
        self.weapon = weapon

        self.autoTalent = auto_talent
        self.autoMVS = None
        self.autoTiming = None
        if weapon_type == ConType.SkillFirst:
            self.skillTalent = skill_talent if constellation < 3 else skill_talent + 3
            self.burstTalent = burst_talent if constellation < 5 else burst_talent + 3
        else:
            self.skillTalent = skill_talent if constellation < 5 else skill_talent + 3
            self.burstTalent = burst_talent if constellation < 3 else burst_talent + 3
        self.constellation = constellation
        self.level = 90
        self.energyCost = energy_cost

        # distribute 2 rolls into each stat
        substatCounts = {Attr(i): 2 for i in range(10)}

        # add rolls to artifact stats
        self.artifactStats += Stats({k: v * substatValues[k] for k, v in substatCounts.items()})

        # add flower and feather
        self.artifactStats += Stats({Attr.ATK: 311, Attr.HP: 4780})
        # add goblet
        self.artifactStats += Stats({elementDict[self.element]: 0.466})

        # add main stats
        self.crCap = 10
        self.cdCap = 10

        self.emblem = False
        self.vv = False
        if len(artifact_set)==0:
            return
        for s in artifact_set:
            match s.set:
                case Set.TF:
                    self.artifactStats[Attr.ELECTRODMG] += 0.15
                case Set.ATK:
                    self.artifactStats[Attr.ATKP] += 0.18
                case Set.TS:
                    if s.count >= 4:
                        self.artifactStats[Attr.DMG] += 0.35
                case Set.GAMBLER:
                    self.artifactStats[Attr.EDMG] += 0.2
                case Set.NO:
                    self.artifactStats[Attr.QDMG] += 0.2
                    if s.count >= 4:
                        delegate = lambda c: actions.Buff(self, c.time,
                                                          buff.Buff(self.noblesseBuff, c.time, 12, self.noblesseID))
                        self.burstCastHook.append(delegate)
                case Set.EMBLEM:
                    self.artifactStats[Attr.ER] += 0.2
                    if s.count >= 4:
                        self.emblem = True
                case Set.VV:
                    self.artifactStats[Attr.ANEMODMG] += 0.15
                    if s.count >= 4:
                        self.vv = True
                        self.artifactStats[Attr.SWIRLBONUS] += 0.6
                case Set.TOM:
                    self.artifactStats[Attr.HPP] += 0.2
                    if s.count >= 4:
                        self.lastTOM = -1
                        """delegate = lambda c: actions.Buff(self, c.time, Buff(self.noblesseBuff, c.time, 3, self.tomID))"""
                        def tom(character):
                            t = character.time
                            if t > character.lastTOM + 0.5:
                                character.rotation.add_event(actions.Buff(self, t, buff.Buff(self.noblesseBuff, t, 3, self.tomID)))

                        self.skillHitHook.append(tom)

    def set_rotation(self, r):
        self.rotation = r

    @abstractmethod
    def normal(self, hits, **kwargs):
        t = self.time
        for i in range(hits):
            t += self.autoTiming[0][i] / 60
            self.rotation.do_damage(self, self.autoMVS[0][i], Element.PHYSICAL, DamageType.NORMAL, t)
            for hook in self.rotation.normalAttackHook:
                hook()

    @abstractmethod
    def charged(self):
        pass

    @abstractmethod
    def skill(self):
        for delegate in self.skillCastHook:
            self.rotation.add_event(delegate(self))

    @abstractmethod
    def burst(self):
        for delegate in self.burstCastHook:
            self.rotation.add_event(delegate(self))

    def reaction(self, reaction):
        if reaction.is_swirl():
            element = reaction.element()
            self.rotation.do_damage(self, 1.2, element, DamageType.REACTION, aoe=True, reaction=reaction)
            # i shouldn't hard code this but i care more about being done than writing good code rn
            # TODO: this is applying to the initial reaction causing it which is wrong but probably not a big deal
            if self.vv and self.rotation.onField == self:
                for e in self.rotation.enemies:
                    e.add_shred(ResShred(element, -0.4, self.time + 10, self.vvID))
            return
        match reaction:
            case Reactions.OVERLOAD:
                self.rotation.do_damage(self, 4, Element.PYRO, DamageType.REACTION, aoe=True,
                                        reaction=Reactions.OVERLOAD)
            case Reactions.EC:
                self.rotation.do_damage(self, 2.4, Element.ELECTRO, DamageType.REACTION,
                                        aoe=True,reaction=Reactions.EC)
            case Reactions.SUPERCONDUCT:
                self.rotation.do_damage(self, 1, Element.CRYO, DamageType.REACTION,
                                        aoe=True, reaction=Reactions.SUPERCONDUCT)
                for e in self.rotation.enemies:
                    e.add_shred(ResShred(Element.PHYSICAL, -0.4, self.time + 12, self.vvID))

    def get_stats(self, time=None):
        if time is None:
            time = self.time
        b = Stats()
        for buff in self.buffs:
            b += buff.buff()
        stats = self.stats + self.weapon.get_stats(time) + self.artifactStats + b
        #print(self, time, self.buffs)
        return stats

    def add_buff(self, buff):
        # TODO: make this not suck
        for i in range(len(self.buffs)):
            other = self.buffs[i]
            if buff == other:
                self.buffs[i] = buff + other
                return
        else:
            self.buffs.append(buff)
        #[other if buff!=other else other+buff for other in self.buffs]


    def remove_buff(self, buff):
        try:
            self.buffs.remove(buff)
            return True
        except ValueError:
            return False

    # mfw i try to change an array while iterating over it
    # i love list comprehension
    def remove_expired_buffs(self):
        self.buffs = [buff for buff in self.buffs if not buff.is_expired(self.rotation)]

    def __repr__(self):
        return str(self.__class__.__name__)

    @property
    def time(self):
        return self.rotation.time

    def do_damage(self, mv, element, damage_type, time=None, aoe=False, debug=False, stats_ref=None):
        self.rotation.do_damage(self, mv, element, damage_type, time, aoe, None, debug, stats_ref)

    def swap_off(self):
        pass