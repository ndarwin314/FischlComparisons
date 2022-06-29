from abc import ABC, abstractmethod
import numpy as np
import attributes
from attributes import Attr, Stats, ArtifactSlots, DamageType, Element, Reactions
from artifacts import Set, SetCount
import weapons
import rotation as rot
from summon import Summon
from enemy import ResShred
from buff import Buff, PermanentBuff
from uuid import uuid4 as uuid
from enum import Enum
import math
import actions


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
        self.weapon = None
        weapon.equip(self)
        self.autoTalent = auto_talent
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
                                                          Buff(self.noblesseBuff, c.time, 12, self.noblesseID))
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
                                character.rotation.add_event(actions.Buff(self, t, Buff(self.noblesseBuff, t, 3, self.tomID)))

                        self.skillHitHook.append(tom)

    def set_rotation(self, r):
        self.rotation = r

    @abstractmethod
    def normal(self, stats, hit):
        pass

    @abstractmethod
    def charged(self, stats):
        pass

    @abstractmethod
    def skill(self, stats):
        for delegate in self.skillCastHook:
            self.rotation.add_event(delegate(self))

    @abstractmethod
    def burst(self, stats):
        for delegate in self.burstCastHook:
            self.rotation.add_event(delegate(self))

    def reaction(self, stats, reaction):
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
        def __init__(self, mv, statsRef, who_summoned, start, duration, con, rotation):
            super().__init__(None, who_summoned, start, duration, rotation)
            self.mv = mv
            self.lastA4 = start
            self.con = con
            self.statsRef = statsRef
            # technically this could change over the burst (sara c6) but i'm not including anything that will so idc

        def on_frame(self):
            if (self.rotation.frame - math.ceil(60 * self.start)) % 60 == 0:
                self.rotation.do_damage(self.summoner, self.mv, Element.ELECTRO, debug=True,
                                        damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)

        def c6(self):
            self.rotation.do_damage(self.summoner, 0.3, Element.ELECTRO,
                                    damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)

        def a4(self, character):
            # TODO: make only off field
            # TODO: make it only apply to electro reactions
            if self.rotation.time > self.lastA4 + 0.5 and self.rotation.onField == self.rotation.characters[character]:
                self.rotation.do_damage(self.summoner, 0.8, Element.ELECTRO,
                                        damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)
                self.lastA4 = self.time

        def summon(self):
            super().summon()
            self.stats = self.statsRef()
            if self.con >= 6:
                self.rotation.normalAttackHook.append(self.c6)
            self.rotation.reactionHook.append(self.a4)

        def recall(self):
            super().recall()
            if self.con >= 6:
                self.rotation.normalAttackHook.remove(self.c6)
            self.rotation.reactionHook.remove(self.a4)

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=weapons.AlleyHunter(refinement=1), artifact_set=(SetCount(Set.ATK, 2), SetCount(Set.ATK, 2)),
                 gambler_slots=None):
        super().__init__(Stats({Attr.HPBASE: 9189,
                                Attr.ATKBASE: 244,
                                Attr.DEFBASE: 594,
                                Attr.ATKP: 0.24,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1}),
                         Element.ELECTRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.SkillFirst, 60)
        self.turretHits = 10 if constellation < 6 else 12
        self.skillTurret = self.skillTurretBase * scalingMultiplier[skill_talent]
        self.skillCast = self.skillCastBase * scalingMultiplier[skill_talent] + (2 if constellation > 1 else 0)
        self.n1 = self.n1Base * autoMultiplier[auto_talent]
        self.aim = self.aimBase * autoMultiplier[auto_talent]
        # technically c4 is a separate damage instance, but it does not make a big difference
        self.burstMV = self.burstBase * scalingMultiplier[burst_talent] + (2.22 if constellation > 3 else 0)

        # artifacts
        self.artifactStats[Attr.ATKP] += 0.466
        stats = self.get_stats(0)
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        self.artifactStats[Attr.CR] += self.crCap * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += self.cdCap * substatValues[Attr.CD]
        self.artifactStats[Attr.ATKP] += 2 * substatValues[Attr.ATKP]

    def normal(self, stats, hit):
        super().normal(stats, hit)
        # TODO: add c1 loser
        self.rotation.do_damage(self, self.n1, Element.PHYSICAL, DamageType.NORMAL)

    def charged(self, stats):
        super().charged(stats)
        self.rotation.do_damage(self, self.aim, Element.PHYSICAL, DamageType.CHARGED)

    def skill(self, stats):
        super().skill(stats)
        self.rotation.do_damage(self, self.skillCast, self.element, DamageType.SKILL, time=self.time + 0.6)
        # self.rotation.add_summon(self.Oz(self.skillTurret, self.get_stats(), self, self.time+1.6, self.turretHits))
        self.rotation.add_event(actions.Summon(self, self.time + .6,
                                               self.Oz(self.skillTurret, lambda :self.get_stats(self.time),
                                                       self, self.time + .6, self.turretHits, self.constellation,
                                                       self.rotation)))

    def burst(self, stats):
        super().burst(stats)
        self.rotation.do_damage(self, self.burstMV , self.element, DamageType.BURST, time=self.time + 0.24,
                                aoe=True)
        self.rotation.add_event(actions.Summon(self, self.time + .4,
                                               self.Oz(self.skillTurret, lambda :self.get_stats(self.time),
                                                       self, self.time + .4, self.turretHits, self.constellation,
                                                       self.rotation)))


class Bennett(Character):
    skillBase = 1.376
    n1Base = 0.4455
    burstBase = 2.328
    atkBuffRatio = [0, .56, .602, .644, .7, .742, .784, .84, .896, .952, 1.008, 1.064, 1.12, 1.19]
    buffID = uuid()

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=weapons.AlleyFlash(), artifact_set=(SetCount(Set.NO, 4),)):
        super().__init__(Stats({Attr.HPBASE: 12397,
                                Attr.ATKBASE: 191,
                                Attr.DEFBASE: 771,
                                Attr.ER: 1.267,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.PYRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.SkillFirst, 60)
        self.skillBase = self.skillBase * scalingMultiplier[skill_talent]
        self.burstBase = self.burstBase * scalingMultiplier[burst_talent]
        self.n1 = self.n1Base * autoMultiplier[auto_talent]
        self.buffValue = (self.atkBuffRatio[self.burstTalent] + (0.2 if constellation >= 1 else 0)) \
                         * self.get_stats(0)[Attr.ATKBASE]
        self.buffStats = Stats({Attr.ATK: self.buffValue})
        if constellation >= 6:
            self.buffStats += Stats({Attr.PYRODMG: 0.15})
        # TODO: fix this to make it more correct
        self.buffCreator = lambda t: actions.Buff(self, t, Buff(self.buffStats, t, 2.1, self.buffID), True)
        self.artifactStats[Attr.ER] += 0.518
        stats = self.get_stats(0)
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        self.artifactStats[Attr.CR] += (self.crCap - 1) * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += (self.cdCap - 1) * substatValues[Attr.CD]
        self.artifactStats[Attr.ER] += 4 * substatValues[Attr.ER]

    def normal(self, stats, hit):
        super().normal(stats, hit)
        self.rotation.do_damage(self, self.n1, Element.PHYSICAL, DamageType.NORMAL)

    def charged(self, stats):
        raise NotImplementedError

    def skill(self, stats):
        super().skill(stats)
        self.rotation.do_damage(self, self.skillBase, self.element, damage_type=DamageType.SKILL,
                                time=self.time + 0.27)

    def burst(self, stats):
        super().burst(stats)
        # TODO maybe: bennett burst in game take several ticks to apply which isn't represented with this currently
        self.rotation.do_damage(self, self.burstBase, self.element, DamageType.BURST, aoe=True,
                                time=self.time + 0.62, stats_ref= lambda : self.get_stats())

        self.rotation.add_event(self.buffCreator(self.time))
        for i in range(13):
            self.rotation.add_event(self.buffCreator(self.time + 0.57 + i))


class Raiden(Character):
    skillcastHookBase = 1.172
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
        def __init__(self, mv, stats, who_summoned, start, rotation):
            super().__init__(stats, who_summoned, start, 25.28, rotation)
            self.mv = mv
            self.lastHit = start + 0.9

        def coordinated_attack(self):
            if self.time > self.lastHit + 0.9:
                self.lastHit = self.time
                self.rotation.do_damage(self.summoner, self.mv, Element.ELECTRO, damage_type=DamageType.SKILL,
                                        time=self.time + 0.09, stats_ref=lambda : self.summoner.get_stats())

        def summon(self):
            super().summon()
            self.rotation.damageHooks.append(self.coordinated_attack)
            for char in self.rotation.characters:
                char.add_buff(PermanentBuff(Stats({Attr.QDMG: 0.003 * char.energyCost}), self.buffID))

        def recall(self):
            super().recall()
            self.rotation.damageHooks.remove(self.coordinated_attack)
            for char in self.rotation.characters:
                char.remove_buff(PermanentBuff(Stats(), self.buffID))

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=weapons.Catch(), artifact_set=(SetCount(Set.EMBLEM, 4),)):
        super().__init__(Stats({Attr.HPBASE: 12907,
                                Attr.ATKBASE: 337,
                                Attr.DEFBASE: 789,
                                Attr.ER: 1.32,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.ELECTRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)
        # TODO: add stuff for cons if i care
        self.resolve = 0
        self.burstActive = False
        self.burstExpiration = 0
        self.autoMVS = self.autoBase * autoMultiplier[self.autoTalent]
        self.infusedMVS = self.autoInfuseBase * physHighMultiplier[self.burstTalent]
        self.skillCastMV = self.skillcastHookBase * scalingMultiplier[self.skillTalent]
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
    def normal(self, stats, hit):
        super().normal(stats, hit)
        # TODO: refactor this
        if self.burstActive and self.time > self.burstExpiration:
            self.burstActive = False
            self.resolve = 0
        if self.burstActive:
            mv = self.infusedMVS[hit] + self.resolve * self.infusedBonusMV
            self.rotation.do_damage(self, mv, self.element, DamageType.BURST)

        else:
            self.rotation.do_damage(self, self.autoMVS[hit], Element.PHYSICAL, DamageType.NORMAL)

    def charged(self, stats):
        super().charged(stats)
        if self.burstActive and self.time > self.burstExpiration:
            self.burstActive = False
            self.resolve = 0
        if self.burstActive:
            # this is a hack to add both mvs together since i'm lazy and they are simultaneous
            mv = self.infusedMVS[-1] + self.infusedMVS[-2] + 2 * self.resolve * self.infusedBonusMV
            self.rotation.do_damage(self, mv, self.element, DamageType.BURST)

        else:
            self.rotation.do_damage(self, self.autoMVS[-1], Element.PHYSICAL, DamageType.CHARGED)

    def skill(self, stats):
        super().skill(stats)
        self.rotation.do_damage(self, self.skillCastMV, self.element, damage_type=DamageType.SKILL,
                                time=self.time + 0.85)
        self.rotation.add_summon(self.NotOz(self.skillTurretMV, stats, self, self.time, self.rotation))

    def burst(self, stats):
        super().burst(stats)
        self.burstActive = True
        # 115 frames of startup plus 7 seconds of burst plus hitlag
        # TODO: how much does hitlag add
        self.burstExpiration = self.time + 115 / 60 + 7 + 2
        # stacks from 1
        self.resolve += 3 * 2
        mv = self.burstMV + self.burstBonusMV * max(self.resolve, 60)
        # there is a problem wherein if a burst is used between this being called and the burst hit the resolve won't count
        # but that is impossible in game anyway so idc
        self.rotation.do_damage(self, mv, self.element, DamageType.BURST, self.time + 1.63, aoe=True)

    def add_resolve(self, cost):
        # TODO: change multiplier to be correct for other talent levels
        self.resolve += cost * 0.19

    def get_stats(self, time=None):
        stats = super().get_stats(time)
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

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=weapons.IronSting(), artifact_set=(SetCount(Set.VV, 4),)):
        super().__init__(Stats({Attr.HPBASE: 13348,
                                Attr.ATKBASE: 297,
                                Attr.DEFBASE: 807,
                                Attr.EM: 115.2,
                                Attr.ER: 1,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.ANEMO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)
        # TODO: add stuff cor cons if i care
        self.burstCast = self.burstCastBase * scalingMultiplier[burst_talent]
        self.burstDOT = self.burstDOTBase * scalingMultiplier[burst_talent]
        self.burstInfuseDOT = self.burstInfuseDOTBase * scalingMultiplier[burst_talent]
        self.skillHold = self.skillHoldBase * scalingMultiplier[skill_talent]
        self.skillPress = self.skillPressBase * scalingMultiplier[skill_talent]
        self.lowPlunge = self.lowPlungeBase * scalingMultiplier[auto_talent]
        self.highPlunge = self.highPlungeBase * scalingMultiplier[auto_talent]

        # artifacts stats
        self.artifactStats[Attr.ANEMODMG] -= 0.466
        # TODO: probably make a method to add substats
        self.artifactStats[Attr.EM] += 187 * 3 + 4 * substatValues[Attr.EM]
        self.artifactStats[Attr.ER] += 10 * substatValues[Attr.ER]
        self.artifactStats[Attr.ATKP] += 6 * substatValues[Attr.ATKP]

    def normal(self, stats, hit):
        raise NotImplemented("why")

    def charged(self, stats):
        raise NotImplemented("why")

    def skill(self, stats, **kwargs):
        super().skill(stats)
        # TODO: tap/hold
        infusion = kwargs["infusion"]
        stats = self.get_stats(self.rotation)
        time = self.time + 0.23
        # chiha whatever
        self.rotation.do_damage(self, self.skillPress, self.element, DamageType.SKILL, time, True)
        time += 0.8
        # a1
        self.rotation.do_damage(self, 2, infusion, DamageType.PLUNGE, time, True)
        # plunge
        self.rotation.do_damage(self, self.highPlunge, self.element, DamageType.PLUNGE, time, True)

    def burst(self, stats, **kwargs):
        super().burst(stats)
        element = kwargs["infusion"]
        t = self.time + 93 / 60
        self.rotation.do_damage(self, self.burstCast, self.element, DamageType.BURST, t, True)
        t += 1.08
        for i in range(4):
            t += 1.95
            self.rotation.do_damage(self, self.burstDOT, self.element, DamageType.BURST, t, True)
            self.rotation.do_damage(self, self.burstInfuseDOT, element, DamageType.BURST, t, True)

    def reaction(self, stats, reaction):
        super().reaction(stats, reaction)
        if reaction.is_swirl():
            element = reaction.element()
            dmgBonus = Stats({attributes.elementDict[element]: self.get_stats(self.time)[Attr.EM] * 0.0004})
            self.rotation.add_event(actions.Buff(self, self.time, Buff(dmgBonus, self.time, 8, self.buffIDS[element])))
