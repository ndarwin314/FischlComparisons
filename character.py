from abc import ABC, abstractmethod
import numpy as np

import attributes
from attributes import Attr, Stats, ArtifactSlots, DamageType, Element, Reactions
from artifacts import Set, SetCount
import weapons
import rotation as r
from summon import Summon
from enemy import ResShred
from buff import Buff, PermanentBuff, StackableBuff
from uuid import uuid4 as uuid
from enum import Enum
import math


class ConType(Enum):
    SkillFirst = 0
    BurstFirst = 0


"""mainStats = {ArtifactSlots.FLOWER: Attr.HP,
             ArtifactSlots.FEATHER: Attr.ATK,
             ArtifactSlots.SANDS: Attr.ATKP,
             ArtifactSlots.GOBLET: Attr.ELEMENTDMG}"""
mainStatValues = {ArtifactSlots.FLOWER: 4780,
                  ArtifactSlots.FEATHER: 311,
                  ArtifactSlots.SANDS: 0.466,
                  ArtifactSlots.GOBLET: 0.466,
                  ArtifactSlots.CIRCLET: 0.311}

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

    def __init__(self, stats, element, autoTalent, skillTalent, burstTalent,
                 constellation, weapon, artifact_set, type, energyCost):
        self.stats = stats
        self.buffs = []
        self.artifactStats = Stats()
        self.element = element
        self.weapon = weapon
        self.autoTalent = autoTalent
        if type == ConType.SkillFirst:
            self.skillTalent = skillTalent if constellation < 3 else skillTalent + 3
            self.burstTalent = burstTalent if constellation < 5 else burstTalent + 3
        else:
            self.skillTalent = skillTalent if constellation < 5 else skillTalent + 3
            self.burstTalent = burstTalent if constellation < 3 else burstTalent + 3
        self.constellation = constellation
        self.level = 90
        self.burstActivated = []
        self.energyCost = energyCost
        self.skillHit = []
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
        for set in artifact_set:
            match set.set:
                case Set.TF:
                    self.artifactStats[Attr.ELECTRODMG] += 0.15
                case Set.ATK:
                    self.artifactStats[Attr.ATKP] += 0.18
                case Set.TS:
                    if set.count >= 4:
                        self.artifactStats[Attr.DMG] += 0.35
                case Set.GAMBLER:
                    self.artifactStats[Attr.EDMG] += 0.2
                case Set.NO:
                    self.artifactStats[Attr.QDMG] += 0.2
                    if set.count >= 4:
                        delegate = lambda t: r.Buff(self, t, Buff(self.noblesseBuff, t, 12, self.noblesseID))
                        self.burstActivated.append(delegate)
                case Set.EMBLEM:
                    self.artifactStats[Attr.ER] += 0.2
                    if set.count >= 4:
                        self.emblem = True
                case Set.VV:
                    self.artifactStats[Attr.ANEMODMG] += 0.15
                    if set.count >= 4:
                        self.vv = True
                        self.artifactStats[Attr.SWIRLBONUS] += 0.6
                case Set.TOM:
                    self.artifactStats[Attr.HPP] += 0.2
                    if set.count >= 4:
                        self.lastTOM = -1

                        def TOM(rotation, character):
                            t = rotation.time
                            if t > character.lastTOM + 0.5:
                                rotation.add_event(r.Buff(self, t, StackableBuff(self.noblesseBuff, 3, t, 3, self.tomID)))
                        self.skillHit.append(TOM)

    @abstractmethod
    def normal(self, stats, rotation, hit):
        return stats.get_attack() * stats.get_crit_multiplier(damageType=DamageType.NORMAL) * \
               stats.get_DMG(Element.PHYSICAL, damageType=DamageType.NORMAL)

    @abstractmethod
    def charged(self, stats, rotation):
        return stats.get_attack() * stats.get_crit_multiplier(damageType=DamageType.CHARGED) * \
               stats.get_DMG(Element.PHYSICAL, damageType=DamageType.CHARGED)

    @abstractmethod
    def skill(self, stats, rotation):
        return stats.get_attack() * stats.get_crit_multiplier(damageType=DamageType.SKILL) * \
               stats.get_DMG(self.element, damageType=DamageType.SKILL)

    @abstractmethod
    def burst(self, stats, rotation):
        for delegate in self.burstActivated:
            rotation.add_event(delegate(rotation.time))
        return stats.get_attack() * stats.get_crit_multiplier(damageType=DamageType.BURST) * \
               stats.get_DMG(self.element, damageType=DamageType.BURST, emblem=self.emblem)

    def reaction(self, stats, rotation, reaction):
        multiplier = stats.transformative_multiplier(reaction)
        if reaction.is_swirl():
            element = reaction.element()
            rotation.do_damage(self, multiplier * 1.2, element, DamageType.REACTION, aoe=True, is_reaction=True)
            # i shouldn't hard code this but i care more about being done than writing good code rn
            # TODO: this is applying to the initial reaction causing it which is wrong but probably not a big deal
            if self.vv:
                for e in rotation.enemies:
                    e.add_shred(ResShred(element, -0.4, rotation.time + 10, self.vvID))
            return
        match reaction:
            case Reactions.OVERLOAD:
                rotation.do_damage(self, multiplier * 4, Element.PYRO, DamageType.REACTION, aoe=True, is_reaction=True)
            case Reactions.EC:
                rotation.do_damage(self, multiplier * 2.4, Element.ELECTRO, DamageType.REACTION, aoe=True, is_reaction=True)
            case Reactions.SUPERCONDUCT:
                rotation.do_damage(self, multiplier, Element.CRYO, DamageType.REACTION, aoe=True, is_reaction=True)
                for e in rotation.enemies:
                    e.add_shred(ResShred(Element.PHYSICAL, -0.4, rotation.time + 12, self.vvID))

    def get_stats(self):
        b = Stats()
        for buff in self.buffs:
            b += buff.buff()
        stats = self.stats + self.weapon.get_stats() + self.artifactStats + b
        return stats

    def add_buff(self, buff):
        for other in self.buffs:
            if buff == other:
                buff += other
                return
        self.buffs.append(buff)

    def remove_buff(self, buff):
        try:
            self.buffs.remove(buff)
            return True
        except ValueError:
            return False

    # mfw i try to change an array while iterating over it
    # i love list comprehension
    def remove_expired_buffs(self, rotation):
        self.buffs = [buff for buff in self.buffs if not buff.is_expired(rotation)]

    def __repr__(self):
        return str(self.__class__.__name__)


class Fischl(Character):
    skillTurretBase = 0.888
    skillCastBase = 1.1544
    n1Base = 0.4412
    burstBase = 2.08
    aimBase = 0.4386

    A4 = 0.8
    C6 = 0.3

    class Oz(Summon):
        # i am ignoring hitlag
        def __init__(self, mv, stats, who_summoned, start, duration, con):
            super().__init__(stats, who_summoned, start, duration)
            self.mv = mv
            self.lastA4 = start
            self.con = con
            # technically this could change over the burst (sara c6) but i'm not including anything that will so idc
            self.multiplier = self.stats.get_crit_multiplier() * self.stats.get_attack() * \
                              (1 + self.stats[Attr.DMG] + self.stats[Attr.ELECTRODMG] + self.stats[Attr.EDMG])

        def on_frame(self, rotation):
            if (rotation.frame - math.ceil(60 * self.start)) % 60 == 0:
                rotation.do_damage(self.summoner, self.mv * self.multiplier, Element.ELECTRO, damage_type=DamageType.SKILL)

        def c6(self, rotation):
            rotation.do_damage(self.summoner, 0.3 * self.multiplier, Element.ELECTRO, damage_type=DamageType.SKILL)

        def a4(self, rotation, character):
            # TODO: make only off field
            # TODO: make it only apply to electro reactions
            if rotation.time > self.lastA4 + 0.5 and rotation.onField == rotation.characters[character]:
                rotation.do_damage(self.summoner, 0.8 * self.multiplier, Element.ELECTRO, damage_type=DamageType.SKILL)
                self.lastA4 = rotation.time

        def summon(self, rotation):
            super().summon(rotation)
            if self.con >= 6:
                rotation.normalAttackHook.append(self.c6)
            rotation.reactionHook.append(self.a4)

        def recall(self, rotation):
            super().recall(rotation)
            if self.con >= 6:
                rotation.normalAttackHook.remove(self.c6)
            rotation.reactionHook.remove(self.a4)

    def __init__(self, autoTalent=9, skillTalent=9, burstTalent=9, constellation=6,
                 weapon=weapons.AlleyHunter(refinement=1), artifact_set=(SetCount(Set.ATK, 2), SetCount(Set.ATK, 2)),
                 gambler_slots=None):
        super().__init__(Stats({Attr.HPBASE: 9189,
                                Attr.ATKBASE: 244,
                                Attr.DEFBASE: 594,
                                Attr.ATKP: 0.24,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1}),
                         Element.ELECTRO, autoTalent, skillTalent, burstTalent,
                         constellation, weapon, artifact_set, ConType.SkillFirst, 60)
        self.turretHits = 10 if constellation < 6 else 12
        self.skillTurret = self.skillTurretBase * scalingMultiplier[skillTalent]
        self.skillCast = self.skillCastBase * scalingMultiplier[skillTalent] + (2 if constellation > 1 else 0)
        self.n1 = self.n1Base * autoMultiplier[autoTalent]
        self.aim = self.aimBase * autoMultiplier[autoTalent]
        # technically c4 is a separate damage instance, but it does not make a big difference
        self.burstMV = self.burstBase * scalingMultiplier[burstTalent] + (2.22 if constellation > 3 else 0)

        # artifacts
        self.artifactStats[Attr.ATKP] += 0.466
        stats = self.get_stats()
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        self.artifactStats[Attr.CR] += self.crCap * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += self.cdCap * substatValues[Attr.CD]
        self.artifactStats[Attr.ATKP] += 2 * substatValues[Attr.ATKP]

    def normal(self, stats, rotation, hit):
        damage = self.n1 * super().normal(stats, rotation, hit)
        # TODO: add c1 loser
        rotation.do_damage(self, damage, Element.PHYSICAL, DamageType.NORMAL)

    def charged(self, stats, rotation):
        damage = self.aim * stats.get_crit_multiplier() * stats.get_attack() * \
                 (1 + stats[Attr.PHYSDMG] + stats[Attr.DMG] + stats[Attr.CADMG])
        rotation.do_damage(self, damage, self.element, DamageType.CHARGED)

    def skill(self, stats, rotation):
        multiplier = super().skill(stats, rotation)
        rotation.do_damage(self, self.skillCast * multiplier, self.element, DamageType.SKILL, time=rotation.time + 0.6)
        # rotation.add_summon(self.Oz(self.skillTurret, self.get_stats(), self, rotation.time+1.6, self.turretHits))
        rotation.add_event(r.Summon(self, rotation.time + 1.6,
                                    self.Oz(self.skillTurret, self.get_stats(),
                                            self, rotation.time + 1.6, self.turretHits, self.constellation)))

    def burst(self, stats, rotation):
        multiplier = super().burst(stats, rotation)
        rotation.do_damage(self, self.burstMV * multiplier, self.element, DamageType.BURST, time=rotation.time + 0.24, aoe=True)
        rotation.add_event(r.Summon(self, rotation.time + 1.4,
                                    self.Oz(self.skillTurret, self.get_stats(),
                                            self, rotation.time + 1.4, self.turretHits, self.constellation)))


class Bennett(Character):
    skillBase = 1.376
    n1Base = 0.4455
    burstBase = 2.328
    atkBuffRatio = [0, .56, .602, .644, .7, .742, .784, .84, .896, .952, 1.008, 1.064, 1.12, 1.19]
    buffID = uuid()

    def __init__(self, autoTalent=9, skillTalent=9, burstTalent=9, constellation=6,
                 weapon=weapons.AlleyFlash(), artifact_set=(SetCount(Set.NO, 4),)):
        super().__init__(Stats({Attr.HPBASE: 12397,
                                Attr.ATKBASE: 191,
                                Attr.DEFBASE: 771,
                                Attr.ER: 1.267,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.PYRO, autoTalent, skillTalent, burstTalent, constellation,
                         weapon, artifact_set, ConType.SkillFirst, 60)
        self.skillBase = self.skillBase * scalingMultiplier[skillTalent]
        self.burstBase = self.burstBase * scalingMultiplier[burstTalent]
        self.n1 = self.n1Base * autoMultiplier[autoTalent]
        self.buffValue = (self.atkBuffRatio[self.burstTalent] + (0.2 if constellation >= 1 else 0)) \
                         * self.get_stats()[Attr.ATKBASE]
        self.buffStats = Stats({Attr.ATK: self.buffValue})
        if constellation >= 6:
            self.buffStats += Stats({Attr.PYRODMG: 0.15})
        # TODO: fix this to make it more correct
        self.buffCreator = lambda t: r.Buff(self, t, Buff(self.buffStats, t, 12, self.buffID))
        self.artifactStats[Attr.ER] += 0.518
        stats = self.get_stats()
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        self.artifactStats[Attr.CR] += (self.crCap - 1) * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += (self.cdCap - 1) * substatValues[Attr.CD]
        self.artifactStats[Attr.ER] += 4 * substatValues[Attr.ER]

    def normal(self, stats, rotation, hit):
        damage = self.n1 * stats.get_crit_multiplier() * stats.get_attack() * \
                 (1 + stats[Attr.PHYSDMG] + stats[Attr.DMG] + stats[Attr.NADMG])
        rotation.do_damage(self, damage, Element.PHYSICAL, DamageType.NORMAL)

    def reaction(self, stats, rotation, reaction):
        super().reaction(stats, rotation, reaction)

    def charged(self, stats, rotation):
        pass

    def skill(self, stats, rotation):
        multiplier = super().burst(stats, rotation)
        rotation.do_damage(self, multiplier * self.skillBase, self.element, damage_type=DamageType.SKILL, time=rotation.time + 0.27)

    def burst(self, stats, rotation):
        # TODO maybe: bennett burst in game take several ticks to apply which isn't represented with this currently
        # buff applies to itself
        stats += self.buffStats
        multiplier = super().burst(stats, rotation)
        print(stats.get_attack() * stats.get_DMG(element=Element.PYRO,
                                                 damageType=DamageType.BURST) * self.burstBase * 19 / 39 * 0.9)
        rotation.do_damage(self, multiplier * self.burstBase, self.element,
                           DamageType.BURST, aoe=True, time=rotation.time + 0.62)
        rotation.add_event(self.buffCreator(rotation.time + 0.62))


class Raiden(Character):
    skillCastBase = 1.172
    skillTurretBase = 0.42
    autoBase = np.array([0.3965, 0.3973, 0.4988, 0.2898, 0.6545, 0.9959])
    burstBase = 4.0080
    burstBaseBonus = 0.0389
    burstAutoBonus = 0.0073
    autoInfuseBase = np.array([0.4474, 0.4396, 0.5382, 0.3089, 0.3098, 0.7394, 0.616, 0.7436])
    autoTimings = [[0.2, 0.35, 0.25, ], [0, 4, 0]]

    class NotOz(Summon):
        offset = 30
        buffID = uuid()

        # i am ignoring hitlag
        def __init__(self, mv, stats, who_summoned, start):
            super().__init__(stats, who_summoned, start, 25.28)
            self.mv = mv
            self.lastHit = start + 0.9

        def coordinated_attack(self, rotation):
            if rotation.time > self.lastHit + 0.9:
                stats = self.summoner.get_stats()
                damage = self.mv * stats.get_attack() * stats.get_crit_multiplier() * \
                         stats.get_DMG(Element.ELECTRO, damageType=DamageType.SKILL)
                self.lastHit = rotation.time
                rotation.do_damage(self.summoner, damage, Element.ELECTRO,
                                   damage_type=DamageType.SKILL, time=rotation.time + 0.09)

        def summon(self, rotation):
            super().summon(rotation)
            rotation.damageHooks.append(self.coordinated_attack)
            for char in rotation.characters:
                char.add_buff(PermanentBuff(Stats({Attr.QDMG: 0.003 * char.energyCost}), self.buffID))

        def recall(self, rotation):
            super().recall(rotation)
            rotation.damageHooks.remove(self.coordinated_attack)
            for char in rotation.characters:
                char.remove_buff(PermanentBuff(Stats(), self.buffID))

    def __init__(self, autoTalent=9, skillTalent=9, burstTalent=9, constellation=0,
                 weapon=weapons.Catch(), artifact_set=(SetCount(Set.EMBLEM, 4),)):
        super().__init__(Stats({Attr.HPBASE: 12907,
                                Attr.ATKBASE: 337,
                                Attr.DEFBASE: 789,
                                Attr.ER: 1.32,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.ELECTRO, autoTalent, skillTalent, burstTalent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)
        # TODO: add stuff cor cons if i care
        self.resolve = 0
        self.burstActive = False
        self.burstExpiration = 0
        self.autoMVS = self.autoBase * autoMultiplier[self.autoTalent]
        self.infusedMVS = self.autoInfuseBase * physHighMultiplier[self.burstTalent]
        self.skillCastMV = self.skillCastBase * scalingMultiplier[self.skillTalent]
        self.skillTurretMV = self.skillTurretBase * scalingMultiplier[self.skillTalent]
        self.burstMV = self.burstBase * scalingMultiplier[self.burstTalent]
        self.burstBonusMV = self.burstBaseBonus * scalingMultiplier[self.burstTalent]
        self.infusedBonusMV = self.burstAutoBonus * scalingMultiplier[self.burstTalent]

        # artifacts
        if isinstance(self.weapon, weapons.Grass):
            self.artifactStats[Attr.ER] += 0.518
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        elif isinstance(self.weapon, weapons.Catch):
            self.artifactStats[Attr.ATKP] += 0.466
            # self.artifactStats[Attr.ER] += 0.518
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        else:
            self.artifactStats[Attr.ATKP] += 0.466
        self.artifactStats[Attr.CR] += self.crCap * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += self.cdCap * substatValues[Attr.CD]
        self.artifactStats[Attr.ER] += 2 * substatValues[Attr.ER]

    # TODO: this doesn't account for multi-hits since i suck
    def normal(self, stats, rotation, hit):
        # TODO: refactor this
        if self.burstActive and rotation.time > self.burstExpiration:
            self.burstActive = False
            self.resolve = 0
        if self.burstActive:
            multiplier = stats.get_crit_multiplier(damageType=DamageType.BURST) * stats.get_attack() * \
                         stats.get_DMG(self.element, damageType=DamageType.BURST, emblem=self.emblem)
            mv = self.infusedMVS[hit] + self.resolve * self.burstAutoBonus
            rotation.do_damage(self, multiplier * mv, self.element, DamageType.BURST)

        else:
            multiplier = super().normal(stats, rotation, hit)
            rotation.do_damage(self, self.autoMVS[hit] * multiplier, Element.PHYSICAL, DamageType.NORMAL)

    def charged(self, stats, rotation):
        if self.burstActive and rotation.time > self.burstExpiration:
            self.burstActive = False
            self.resolve = 0
        if self.burstActive:
            multiplier = stats.get_crit_multiplier(damageType=DamageType.BURST) * stats.get_attack() * \
                         stats.get_DMG(self.element, damageType=DamageType.BURST, emblem=self.emblem)
            # this is a hack to add both mvs together since i'm lazy and they are simultaneous
            mv = self.infusedMVS[-1] + self.infusedMVS[-2] + 2 * self.resolve * self.infusedBonusMV
            rotation.do_damage(self, multiplier * mv, self.element, DamageType.BURST)

        else:
            multiplier = super().charged(stats, rotation)
            rotation.do_damage(self, self.autoMVS[-1] * multiplier, Element.PHYSICAL, DamageType.CHARGED)

    def skill(self, stats, rotation):
        multiplier = super().skill(stats, rotation)
        rotation.do_damage(self, self.skillCastMV * multiplier, self.element, damage_type=DamageType.SKILL, time=rotation.time + 0.85)
        rotation.add_summon(self.NotOz(self.skillTurretMV, stats, self, rotation.time))

    def burst(self, stats, rotation):
        self.burstActive = True
        # 115 frames of startup plus 7 seconds of burst plus hitlag
        # TODO: how much does hitlag add
        self.burstExpiration = rotation.time + 115 / 60 + 7 + 2
        # stacks from self burst and A1
        self.resolve += 17.1 + 3 * 2
        mv = self.burstMV + self.burstBonusMV * max(self.resolve, 60)
        self.resolve -= 17.1
        # there is a problem wherein if a burst is used between this being called and the burst hit the resolve wont count
        # but that is impossible in game anyway so idc
        multiplier = super().burst(stats, rotation)
        rotation.do_damage(self, mv * multiplier, self.element, DamageType.BURST, rotation.time + 1.63, aoe=True)

    def add_resolve(self, cost):
        # change multiplier to be correct for other talent levels
        self.resolve += cost * 0.19

    def get_stats(self):
        stats = super().get_stats()
        a4 = Stats({elementDict[self.element]: (stats[Attr.ER] - 1) * 0.4})
        stats += a4
        return stats


class Kazuha(Character):
    burstCastBase = 2.624
    burstDOTBase = 1.2
    burstInfuseDOTBase = 0.36
    skillPressBase = 1.92
    skillHoldBase = 2.6080
    lowPlungeBase = 1.6363
    highPlungeBase = 2.0439
    buffIDS = {Element.PYRO: uuid(),
               Element.HYDRO: uuid(),
               Element.ELECTRO: uuid(),
               Element.CRYO: uuid()}

    def __init__(self, autoTalent=9, skillTalent=9, burstTalent=9, constellation=0,
                 weapon=weapons.IronSting(), artifact_set=(SetCount(Set.VV, 4),)):
        super().__init__(Stats({Attr.HPBASE: 13348,
                                Attr.ATKBASE: 297,
                                Attr.DEFBASE: 807,
                                Attr.EM: 115.2,
                                Attr.ER: 1,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.ANEMO, autoTalent, skillTalent, burstTalent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)
        # TODO: add stuff cor cons if i care
        self.burstCast = self.burstCastBase * scalingMultiplier[burstTalent]
        self.burstDOT = self.burstDOTBase * scalingMultiplier[burstTalent]
        self.burstInfuseDOT = self.burstInfuseDOTBase * scalingMultiplier[burstTalent]
        self.skillHold = self.skillHoldBase * scalingMultiplier[skillTalent]
        self.skillPress = self.skillPressBase * scalingMultiplier[skillTalent]
        self.lowPlunge = self.lowPlungeBase * scalingMultiplier[autoTalent]
        self.highPlunge = self.highPlungeBase * scalingMultiplier[autoTalent]

        # artifacts stats
        self.artifactStats[Attr.ANEMODMG] -= 0.466
        # TODO: probably make a method to add substats
        self.artifactStats[Attr.EM] += 187 * 3 + 4 * substatValues[Attr.EM]
        self.artifactStats[Attr.ER] += 10 * substatValues[Attr.ER]
        self.artifactStats[Attr.ATKP] += 6 * substatValues[Attr.ATKP]

    def normal(self, stats, rotation, hit):
        raise NotImplemented("why")

    def charged(self, stats, rotation):
        raise NotImplemented("why")

    def skill(self, stats, rotation, **kwargs):
        # TODO: tap/hold
        infusion = kwargs["infusion"]
        stats = self.get_stats()
        atk = stats.get_attack()
        # the only thing that effects skill cr is festering as far as i know so idk
        crit = stats.get_crit_multiplier()
        skillDMG = stats.get_DMG(self.element, damageType=DamageType.SKILL)
        plungeDMG = stats.get_DMG(infusion, damageType=DamageType.PLUNGE)
        time = rotation.time + 0.23
        # chiha whatever
        rotation.do_damage(self, atk * crit * skillDMG * self.skillPress, self.element, DamageType.SKILL, time, True)
        time += 0.8
        # a1
        rotation.do_damage(self, atk * crit * plungeDMG * 2, infusion, DamageType.PLUNGE, time, True)
        # plunge
        rotation.do_damage(self, atk * crit * plungeDMG * self.highPlunge, self.element, DamageType.PLUNGE, time, True)

    def burst(self, stats, rotation, **kwargs):
        element = kwargs["infusion"]
        multiplier = super().burst(stats, rotation)
        infuseMultiplier = stats.get_attack() * stats.get_crit_multiplier(damageType=DamageType.BURST) * \
                           stats.get_DMG(element, damageType=DamageType.BURST)
        t = rotation.time + 93 / 60
        rotation.do_damage(self, multiplier * self.burstCast, self.element, DamageType.BURST, t, True)
        t += 1.08
        for i in range(4):
            t += 1.95
            rotation.do_damage(self, multiplier * self.burstDOT, self.element, DamageType.BURST, t, True)
            rotation.do_damage(self, infuseMultiplier * self.burstInfuseDOT, element, DamageType.BURST, t, True)

    def reaction(self, stats, rotation, reaction):
        super().reaction(stats, rotation, reaction)
        if reaction.is_swirl():
            element = reaction.element()
            dmgBonus = Stats({attributes.elementDict[element]: self.get_stats()[Attr.EM] * 0.0004})
            rotation.add_event(r.Buff(self, rotation.time, Buff(dmgBonus, rotation.time, 8, self.buffIDS[element])))
