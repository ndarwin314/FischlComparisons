from attributes import Element, Reactions, Attr, Stats, DamageType
from enemy import ResShred
from enum import Enum
from abc import ABC, abstractmethod
from statObject import StatObject
from summon import Summon
import math
import numpy as np
import actions
import buff
import mv
from uuid import uuid4 as uuid
import artifacts
import icd
from functools import partial


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
               Element.PHYSICAL: Attr.PHYSDMG,
               Element.DENDRO: Attr.DENDRODMG}
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

physLowMultiplier = [0,
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

physMultiplier = [0,
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

physHighMultiplier = [0,
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

flatMultiplier = [1,
                  1.1,
                  1.208,
                  1.325,
                  1.45,
                  1.583,
                  1.725,
                  1.875,
                  2.033,
                  2.2,
                  2.375,
                  2.559,
                  2.75,
                  2.95,
                  3.159]

lowElemMultiplier = [
    1,
    1.06,
    1.12,
    1.198,
    1.257,
    1.317,
    1.395,
    1.473,
    1.551,
    1.629,
    1.707,
    1.784,
    1.862,
    1.94,
    2.018]

substatValues = {Attr.HPP: 0.0496, Attr.HP: 253.94,
                 Attr.ATKP: 0.0496, Attr.ATK: 16.54,
                 Attr.DEFP: 0.0620, Attr.DEF: 19.68,
                 Attr.EM: 19.82, Attr.ER: 0.051,
                 Attr.CR: 0.0331, Attr.CD: 0.0662}





class Character(StatObject):
    noblesseID = uuid()
    noblesseBuff = Stats({Attr.ATKP: 0.2})
    vvID = uuid()
    tomID = uuid()
    nope = icd.WTF()
    instructorID = uuid()
    shimeID = uuid()

    def __init__(self, stats: Attr, element: Element, auto_talent: int, skill_talent: int, burst_talent: int,
                 constellation: int, weapon: "Weapon", artifact_set: ["SetBase"], weapon_type, energy_cost: int, er_req: float):
        super().__init__(stats, None)
        # TODO: programmatically determine this based on level
        self.levelMultiplier = 725.26

        self.infusion = False

        self.normalICD = icd.ICD(2.5, 3)
        self.icdList = [self.normalICD]

        # hooks
        self.burstCastHook = []
        self.burstHitHook = []
        self.skillCastHook = []
        self.skillHitHook = []
        self.normalHitHook = []
        self.chargedHitHook = []
        self.damageHook = []
        self.healingHook = []
        self.reactionHook = []
        self.swapOnHook = []
        self.swapOffHook = []

        self.artifactStats = Stats()
        self.element = element
        self.weapon = weapon
        self.er_req = er_req
        self.artifact_set = artifact_set

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
        self.lastTOM = -1
        self.lastOHC = -4
        self.OHCMV = mv.MV(flat=0)
        for s in artifact_set:
              s.add(self)

        erSubs = round(max(er_req - self.get_stats(0)[Attr.ER], 0) / substatValues[Attr.ER] + 0.5)
        self.add_substat(Attr.ER, erSubs)
        self.distributedSubs = 20 - erSubs


    def reset(self):
        """self.infusion = False
        self.normalICD = icd.ICD(2.5, 3)
        # hooks
        self.burstCastHook = []
        self.burstHitHook = []
        self.skillCastHook = []
        self.skillHitHook = []
        self.normalHitHook = []
        self.chargedHitHook = []
        self.damageHook = []
        self.healingHook = []
        self.reactionHook = []
        self.swapOnHook = []
        self.swapOffHook = []"""
        self.buffs = []
        self.directBuffs = []
        for icd in self.icdList:
            icd.reset()

    def set_rotation(self, r):
        self.rotation = r
        # TODO so i want to move artifact equipping to here but then that creates an issue with er requirements
        # not counting emblem er so i need to refactor that, but then i need to refactor character code
        # and its a whole deal


    def normal(self, hits, **kwargs):
        # TODO ACTUAL SERIOUS THING, with current implementation multi hit things are fucked and i need to figure out
        # a good way to handle it that doesnt suck
        t = self.time
        charged = kwargs.get("charged")
        if charged is None:
            charged = False
        element = self.element if self.infusion else Element.PHYSICAL
        for i in range(hits):
            t += self.autoTiming[0][i] / 60
            self.do_damage(self.autoMVS[0][i], element, DamageType.NORMAL, t, icd=self.normalICD)
            for hook in self.rotation.normalAttackHook:
                hook(t, self.autoTiming[0][i] / 60)
        if charged:
            for i in range(len(self.autoTiming[1])):
                t += self.autoTiming[1][i] / 60
                self.do_damage(self.autoMVS[1][i], element, DamageType.CHARGED, t, icd=self.normalICD)
                for hook in self.rotation.chargedAttackHook:
                    hook(t, self.autoTiming[0][i] / 60)

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

    def end_infusion(self):
        self.infusion = False

    def reaction(self, reaction, **kwargs):
        if reaction.is_swirl():
            element = reaction.element()
            self.do_damage(mv.MV(flat=1.2*self.levelMultiplier*(2 if self.rotation.enemyCount>1 else 1)), element, DamageType.REACTION, aoe=True, reaction=reaction, icd=Character.nope)
            # i shouldn't hard code this but i care more about being done than writing good code rn
            # TODO: this is applying to the initial reaction causing it which is wrong but probably not a big deal
            if self.vv and self.rotation.onField == self:
                shred = ResShred(element, -0.4, self.time + 10, self.vvID)
                self.rotation.add_event(actions.ResShred(self, self.time + 1/60, shred))
            return
        match reaction:
            case Reactions.OVERLOAD:
                self.do_damage(mv.MV(flat=4*self.levelMultiplier), Element.PYRO, DamageType.REACTION, aoe=True,
                                        reaction=Reactions.OVERLOAD, icd=Character.nope)
            case Reactions.EC:
                self.do_damage(mv.MV(flat=2.4*self.levelMultiplier), Element.ELECTRO, DamageType.REACTION,
                                        aoe=True,reaction=Reactions.EC, icd=Character.nope)
            case Reactions.SUPERCONDUCT:
                self.do_damage(mv.MV(flat=1*self.levelMultiplier), Element.CRYO, DamageType.REACTION,
                                        aoe=True, reaction=Reactions.SUPERCONDUCT, icd=Character.nope)
                for e in self.rotation.enemies:
                    e.add_shred(ResShred(Element.PHYSICAL, -0.4, self.time + 12, self.vvID))

    def get_stats(self, time=None):
        try:
            if time is None:
                time = self.time
        except AttributeError:
            time = 0
        b = Stats()
        for buff_ in self.buffs:
            b += buff_.buff()
        stats = self.stats + self.weapon.get_stats(time) + self.artifactStats + b
        return stats

    def is_on_field(self):
        return self == self.rotation.onField

    def add_buff(self, b: buff.Buff):
        # probably refactor this so the logic for adding buffs is handled by the buff and not the character
        buffList = self.directBuffs if isinstance(b, buff.DirectGenericBuff) else self.buffs
        for i in range(len(buffList)):
            other = buffList[i]
            if b == other:
                buffList[i] = b + other
                return
        else:
            buffList.append(b)
        #[other if buff!=other else other+buff for other in self.buffs]

    def remove_buff(self, b: buff.Buff):
        buffList = self.directBuffs if isinstance(b, buff.DirectGenericBuff) else self.buffs
        try:
            buffList.remove(buff)
            return True
        except ValueError:
            return False

    def add_substat(self, sub: Attr, rolls: int=1):
        self.artifactStats[sub] += rolls * substatValues[sub]


    def remove_substat(self, sub: Attr, rolls: int=1):
        self.artifactStats[sub] -= rolls * substatValues[sub]

    def remove_buff(self, buff: buff.Buff):
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

    def do_damage(self, mv, element, damage_type, time=None, aoe=False, debug=False, stats_ref=None, reaction=None, icd=None):
        self.rotation.do_damage(self, mv, element, damage_type, time, aoe, reaction, debug, stats_ref, icd)

    def swap_off(self):
        for delegate in self.swapOffHook:
            delegate(self)

    def swap_on(self):
        for delegate in self.swapOnHook:
            delegate(self)

    def get_parent_stats(self, time):
        return self.get_stats(time)