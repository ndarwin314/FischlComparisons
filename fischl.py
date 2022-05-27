import attributes
from attributes import Attr, Stats, ArtifactSlots
import bows
from enum import Enum
from functools import cache


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

autoMultiplier = [1,
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
substatValues = {Attr.HPP: 0.0496, Attr.HP: 253.94,
                 Attr.ATKP: 0.0496, Attr.ATK: 16.54,
                 Attr.DEFP: 0.0620, Attr.DEF: 19.68,
                 Attr.EM: 19.82, Attr.ER: 0.051,
                 Attr.CR: 0.0331, Attr.CD: 0.0662}


class Set(Enum):
    TF = 0
    ATK = 1
    TS = 2
    G = 3


class Fischl:
    skillTurretBase = 0.888
    skillCastBase = 1.1544
    n1Base = 0.4412
    burstBase = 2.08
    aimBase = 0.4386

    A4 = 0.8
    C6 = 0.3

    mainStats = {ArtifactSlots.FLOWER: Attr.HP,
                 ArtifactSlots.FEATHER: Attr.ATK,
                 ArtifactSlots.SANDS: Attr.ATKP,
                 ArtifactSlots.GOBLET: Attr.ELEMENTDMG}
    mainStatValues = {ArtifactSlots.FLOWER: 4780,
                      ArtifactSlots.FEATHER: 311,
                      ArtifactSlots.SANDS: 0.466,
                      ArtifactSlots.GOBLET: 0.466,
                      ArtifactSlots.CIRCLET: 0.311}

    def __init__(self, autoTalent, skillTalent, burstTalent, constellation, weapon, artifact_set=(Set.TF, Set.ATK),
                 gambler_slots=None):
        skillTalent = skillTalent if constellation < 3 else skillTalent + 3
        burstTalent = burstTalent if constellation < 5 else burstTalent + 3
        self.constellation = constellation
        self.skillTurret = self.skillTurretBase * scalingMultiplier[skillTalent]
        self.skillCast = self.skillCastBase * scalingMultiplier[skillTalent] + (2 if constellation > 1 else 0)
        self.n1 = self.n1Base * autoMultiplier[autoTalent]
        self.aim = self.aimBase * autoMultiplier[autoTalent]
        # technically c4 is a separate damage instance but it does not make a big difference
        self.burst = self.burstBase * scalingMultiplier[burstTalent] + (2.22 if constellation > 3 else 0)
        self.level = 90
        self.turretHits = 10 if constellation < 6 else 12
        self.stats = Stats({Attr.HPBASE: 9189, Attr.ATKBASE: 244, Attr.DEFBASE: 594, Attr.ATKP: 0.24,
                            Attr.CR: 0.05, Attr.CD: 0.5, Attr.ER: 1})
        self.buffs = Stats()
        self.artifactStats = Stats()
        self.fourStarRolls = 0
        self.fourStarSlots = gambler_slots
        self.gambler = False
        for SET in artifact_set:
            match SET:
                case Set.TF:
                    self.artifactStats[Attr.ELEMENTDMG] += 0.15
                case Set.ATK:
                    self.artifactStats[Attr.ATKP] += 0.18
                case Set.TS:
                    self.artifactStats[Attr.DMG] += 0.35
                case Set.G:
                    self.artifactStats[Attr.EDMG] += 0.2
                    # kqm standards assume 40 susbtats which is 8 per artifact which is min
                    # so for four-star artifacts i assume 6 rolls which is min
                    self.fourStarRolls = 12
                    self.gambler = True
        self.weapon = weapon
        self.resMultiplier = 0.9
        self.defMultiplier = 19 / 39

    def reset(self):
        self.buffs = Stats()
        self.weapon.conditionalStats = Stats()
        self.resMultiplier = 0.9

    #@cache
    def get_stats(self):
        return self.stats + self.buffs + self.weapon.get_stats() + self.artifactStats

    def kqm_optimize(self, rotation, er_requirement=1, sweaty=False):

        # distribute 2 rolls into each stat
        # for generosity assume that half the four-star rolls are here and are into bad stats
        substatCounts = {Attr(i): 2 for i in range(10)}

        # add rolls to artifact stats
        self.artifactStats += Stats({k: v * substatValues[k] for k, v in substatCounts.items()})

        # deduct rolls for 4* artifact
        substatRolls = 20 - 4 * self.gambler

        # add main stats
        crCap = 10
        cdCap = 10
        for slot in ArtifactSlots:
            if self.gambler and slot in self.fourStarSlots:
                m = attributes.fourStarMultiplier
            else:
                m = 1
            if slot == ArtifactSlots.CIRCLET:
                currentStats = self.get_stats()
                if currentStats[Attr.CD] > 2 * currentStats[Attr.CR]:
                    self.artifactStats[Attr.CR] += 0.311 * m
                    crCap -= 2
                else:
                    self.artifactStats[Attr.CD] += 0.622 * m
                    cdCap -= 2
            else:
                self.artifactStats[self.mainStats[slot]] += self.mainStatValues[slot] * m

        # distribute enough ER rolls
        currentStats = self.get_stats()
        while currentStats[Attr.ER] + substatCounts[Attr.ER] * substatValues[Attr.ER] < er_requirement:
            substatCounts[Attr.ER] += 1
            substatRolls -= 1
            if substatRolls == 0:
                pass


        # greedy algorithm search for good substats
        goodSubstats = {Attr.CR: crCap, Attr.CD: cdCap, Attr.ATKP: 8, Attr.EM: 10}
        bestDamage = 0
        bestRoll = None
        m = 1
        for i in range(substatRolls):
            # distribute last 6 stats as lowered value because four-star
            if i == substatRolls - 6 and self.gambler:
                m = 0.8
            for k, v in goodSubstats.items():
                value = m * substatValues[k]
                self.artifactStats[k] += value
                damage = rotation(sweaty=sweaty)
                if bestDamage < damage:
                    bestDamage = damage
                    bestRoll = k
                self.artifactStats[k] -= value
            self.artifactStats[bestRoll] += m * substatValues[bestRoll]
            goodSubstats[bestRoll] -= 1
            # if you run out of allotted rolls, remove that stat
            if goodSubstats[bestRoll] <= 0:
                goodSubstats.pop(bestRoll)
        return round(rotation(sweaty=sweaty), 2)

    def proc_damage(self, stats, chances=1):
        # currently assuming no phys shred
        return self.weapon.damage_proc(stats, chances) * 0.9 * self.defMultiplier

    def burst_damage(self, stats, targets=1):
        return self.burst * stats.get_crit_multiplier() * stats.get_attack() * targets * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.QDMG]) * \
               self.resMultiplier * self.defMultiplier

    def n1_damage(self, stats):
        return self.n1 * stats.get_crit_multiplier() * stats.get_attack() * \
               (1 + stats[Attr.PHYSDMG] + stats[Attr.DMG] + stats[Attr.NADMG]) * \
               self.resMultiplier * self.defMultiplier

    def aim_damage(self, stats):
        return self.aim * stats.get_crit_multiplier() * stats.get_attack() * \
               (1 + stats[Attr.PHYSDMG] + stats[Attr.DMG] + stats[Attr.CADMG]) * \
               self.resMultiplier * self.defMultiplier

    def turret_damage(self, stats, hits):
        return self.skillTurret * stats.get_crit_multiplier() * stats.get_attack() * hits * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * \
               self.resMultiplier * self.defMultiplier

    def skill_cast(self, stats, targets=1):
        return self.skillCast * stats.get_crit_multiplier() * stats.get_attack() * targets * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * \
               self.resMultiplier * self.defMultiplier

    def a4_damage(self, stats):
        return self.A4 * stats.get_crit_multiplier() * stats.get_attack() * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * \
               self.resMultiplier * self.defMultiplier

    def c6_damage(self, stats):
        return self.C6 * stats.get_crit_multiplier() * stats.get_attack() * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * \
               self.resMultiplier * self.defMultiplier

    def ec_damage(self, stats):
        return 2.4 * self.resMultiplier * stats.transformative_multiplier()

    def ol_damage(self, stats):
        return 4 * self.resMultiplier * stats.transformative_multiplier()

    def rotation_sukokomon(self, sweaty=True):
        damage = 0
        if isinstance(self.weapon, bows.AlleyHunter):
            self.weapon.set_stacks(10)
        elif sweaty:
            currentStats = self.get_stats()
            damage += self.n1_damage(currentStats)
            damage += self.aim_damage(currentStats)
            # skyward harp / hunt proc
            # TODO: the formula here is slightly inaccurate since you would have multiple chances to proc the passive
            damage += self.proc_damage(currentStats, 2)
            if isinstance(self.weapon, bows.PrototypeCrescent):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.MitternachtsWaltz):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.PolarStar):
                self.weapon.set_stacks(2)
        currentStats = self.get_stats()
        # use burst
        damage += self.burst_damage(currentStats)
        # average 1 ec proc
        damage += self.ec_damage(currentStats)
        if isinstance(self.weapon, bows.PolarStar):
            # 1 stack from burst
            self.weapon.set_stacks(3 if sweaty else 1)
            currentStats = self.get_stats()

        # Sucrose a1 and a4 and TOTM from kokomi
        self.buffs[Attr.EM] += 200
        self.buffs[Attr.ATKP] += 0.2

        # 2 procs at 10% res and the rest at -30
        damage += self.turret_damage(currentStats, 2)
        self.resMultiplier = 1.15
        damage += self.turret_damage(currentStats, self.turretHits - 2)
        damage += 8 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += 8 * self.a4_damage(currentStats)
        if isinstance(self.weapon, bows.ElegyForTheEnd):
            self.weapon.set_passive(True)
            currentStats = self.get_stats()
        # average 0.6 ec procs at lowered res
        damage += 0.6 * self.ec_damage(currentStats)

        # cast skill after oz duration ends
        if isinstance(self.weapon, bows.PolarStar) and not sweaty:
            self.weapon.set_stacks(1)
        elif sweaty:
            currentStats = self.get_stats()
            damage += self.n1_damage(currentStats)
            damage += self.aim_damage(currentStats)
            # skyward harp / hunt proc
            damage += self.proc_damage(currentStats, 2)
            if isinstance(self.weapon, bows.PrototypeCrescent):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.MitternachtsWaltz):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.PolarStar):
                self.weapon.set_stacks(3)
        currentStats = self.get_stats()
        damage += self.proc_damage(currentStats, 2)
        damage += self.skill_cast(currentStats)
        """if isinstance(self.weapon, bows.WindblumeOde):
            self.weapon.skill_cast(True)
            currentStats = self.get_stats()"""
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += 12 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += 17 * self.c6_damage(currentStats)
        self.reset()
        return damage

    def rotation(self, a4procs=10, c6procs=10, sweaty=True):
        damage = 0
        if isinstance(self.weapon, bows.AlleyHunter):
            self.weapon.set_stacks(10)
        elif sweaty:
            currentStats = self.get_stats()
            damage += self.n1_damage(currentStats)
            damage += self.aim_damage(currentStats)
            # skyward harp / hunt proc
            damage += self.proc_damage(currentStats, 2)
            if isinstance(self.weapon, bows.PrototypeCrescent):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.MitternachtsWaltz):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.PolarStar):
                self.weapon.set_stacks(2)
        # use burst
        currentStats = self.get_stats()
        damage += self.burst_damage(currentStats)
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += a4procs / 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += c6procs / 2 * self.c6_damage(currentStats)

        # cast skill after oz duration ends
        if isinstance(self.weapon, bows.PolarStar) and not sweaty:
            self.weapon.set_stacks(1)
        elif sweaty:
            currentStats = self.get_stats()
            damage += self.n1_damage(currentStats)
            damage += self.aim_damage(currentStats)
            # skyward harp / hunt proc
            damage += self.proc_damage(currentStats, 2)
            if isinstance(self.weapon, bows.PrototypeCrescent):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.MitternachtsWaltz):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.PolarStar):
                self.weapon.set_stacks(3)
        currentStats = self.get_stats()
        damage += self.skill_cast(currentStats)
        """if isinstance(self.weapon, bows.WindblumeOde):
            self.weapon.skill_cast(True)
            currentStats = self.get_stats()"""
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += a4procs / 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += c6procs / 2 * self.c6_damage(currentStats)
        self.reset()
        return damage

    def rotation_raifish(self, sweaty=False):
        damage = 0
        # bennett buffs
        self.buffs[Attr.ATK] = 1119
        self.buffs[Attr.ATKP] = 0.2
        # kazuha buffs
        self.buffs[Attr.ELEMENTDMG] = 0.384
        self.resMultiplier = 1.15
        # raiden buffs
        self.buffs[Attr.QDMG] = 0.18

        if isinstance(self.weapon, bows.AlleyHunter):
            self.weapon.set_stacks(10)
        elif sweaty:
            currentStats = self.get_stats()
            damage += self.n1_damage(currentStats)
            damage += self.aim_damage(currentStats)
            # skyward harp / hunt proc
            damage += self.proc_damage(currentStats, 2)
            if isinstance(self.weapon, bows.PrototypeCrescent):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.MitternachtsWaltz):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.PolarStar):
                self.weapon.set_stacks(2)
        # use burst
        """elif isinstance(self.weapon, bows.ElegyForTheEnd):
            # realistically this is only possible second rotation onward and even then the uptime is sus
            self.weapon.set_passive(True)"""
        currentStats = self.get_stats()
        damage += self.burst_damage(currentStats)
        damage += self.ol_damage(currentStats)
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += 1 * self.a4_damage(currentStats)
        if self.constellation == 6:
            # assuming 3n3c n1c and a one extra proc somewhere
            damage += 11 * self.c6_damage(currentStats)
        if isinstance(self.weapon, bows.ElegyForTheEnd):
            self.weapon.set_passive(True)
            currentStats = self.get_stats()
        # resummon oz before second rotation but only get 5 hits
        if isinstance(self.weapon, bows.PolarStar) and not sweaty:
            self.weapon.set_stacks(1)
        elif sweaty:
            currentStats = self.get_stats()
            damage += self.n1_damage(currentStats)
            damage += self.aim_damage(currentStats)
            # skyward harp / hunt proc
            damage += self.proc_damage(currentStats, 2)
            if isinstance(self.weapon, bows.PrototypeCrescent):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.MitternachtsWaltz):
                self.weapon.set_passive(True)
            elif isinstance(self.weapon, bows.PolarStar):
                self.weapon.set_stacks(3)
        damage += self.skill_cast(currentStats)
        damage += self.turret_damage(currentStats, 5)
        damage += 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += 3 * self.c6_damage(currentStats)

        # second rotation, no fischl e
        damage += self.burst_damage(currentStats)
        if isinstance(self.weapon, bows.SkywardHarp):
            damage += self.proc_damage(currentStats, 2)
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            # assuming 3n3c n1c and a one extra proc somewhere
            damage += 11 * self.c6_damage(currentStats)
        self.reset()
        return damage
