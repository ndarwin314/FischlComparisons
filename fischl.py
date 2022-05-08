from attributes import Attr, Stats
import bows
from enum import Enum

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
substatValues = {Attr.HPP: 0.0496, Attr.HP: 253.94,
                 Attr.ATKP: 0.0496, Attr.ATK: 16.54,
                 Attr.DEFP: 0.0620, Attr.DEF: 19.68,
                 Attr.EM: 19.82, Attr.ER: 0.051,
                 Attr.CR: 0.0331, Attr.CD: 0.0662}

class Set(Enum):
    TF = 0
    ATK = 1
    TS = 2


class Fischl:
    skillTurretBase = 0.888
    skillCastBase = 1.1544
    burstBase = 2.08
    A4 = 0.8
    C6 = 0.3

    def __init__(self, skillTalent, burstTalent, constellation, weapon, artifact_set=(Set.TF, Set.ATK)):
        skillTalent = skillTalent if constellation < 3 else skillTalent + 3
        burstTalent = burstTalent if constellation < 5 else burstTalent + 3
        self.constellation = constellation
        self.skillTurret = self.skillTurretBase * scalingMultiplier[skillTalent]
        self.skillCast = self.skillCastBase * scalingMultiplier[skillTalent] + (2 if constellation > 1 else 0)
        # technically c4 is a separate damage instance but it does not make a big difference
        self.burst = self.burstBase * scalingMultiplier[burstTalent] + (2.22 if constellation > 3 else 0)
        self.level = 90
        self.turretHits = 10 if constellation < 6 else 12
        self.stats = Stats({Attr.HPBASE: 9189, Attr.ATKBASE: 244, Attr.DEFBASE: 594, Attr.ATKP: 0.24,
                            Attr.CR: 0.05, Attr.CD: 0.5, Attr.ER: 1})
        self.buffs = Stats()
        self.artifactStats = Stats({Attr.HP: 4780, Attr.ATK: 311, Attr.ATKP: 0.466, Attr.ELEMENTDMG: 0.466})
        self.weapon = weapon
        self.resMultiplier = 0.9
        for set in artifact_set:
            if set == Set.TF:
                self.artifactStats[Attr.ELEMENTDMG] += 0.15
            elif set == Set.ATK:
                self.artifactStats[Attr.ATKP] += 0.18
            elif set == Set.TS:
                self.artifactStats[Attr.DMG] += 0.35

    def reset(self):
        self.buffs = Stats()
        self.weapon.conditionalStats = Stats()
        self.resMultiplier = 0.9

    def get_stats(self):
        return self.stats + self.buffs + self.weapon.get_stats() + self.artifactStats

    def kqm_optimize(self, rotation, er_requirement=1, sweaty=False):
        # distribute 2 rolls into each stat
        substatCounts = {Attr(i): 2 for i in range(10)}
        currentStats = self.get_stats()
        # distribute enough ER rolls
        substatRolls = 20
        while currentStats[Attr.ER] + substatCounts[Attr.ER] * substatValues[Attr.ER] < er_requirement:
            substatCounts[Attr.ER] += 1
            substatRolls -= 1
            if substatRolls == 0:
                pass

        # add rolls to artifact stats
        self.artifactStats += Stats({k: v * substatValues[k] for k, v in substatCounts.items()})

        # add circlet to balance ratio
        currentStats = self.get_stats()
        crCap = 10
        cdCap = 10
        if currentStats[Attr.CD] > 2 * currentStats[Attr.CR]:
            self.artifactStats[Attr.CR] += 0.311
            crCap -= 2
        else:
            self.artifactStats[Attr.CD] += 0.622
            cdCap -= 2
        # greedy algorithm search for good substats
        goodSubstats = {Attr.CR: crCap, Attr.CD: cdCap, Attr.ATKP: 8, Attr.EM: 10}
        bestDamage = 0
        bestRoll = None
        for i in range(substatRolls):
            for k, v in goodSubstats.items():
                self.artifactStats[k] += substatValues[k]
                damage = rotation(sweaty=sweaty)
                if bestDamage < damage:
                    bestDamage = damage
                    bestRoll = k
                self.artifactStats[k] -= substatValues[k]
            self.artifactStats[bestRoll] += substatValues[bestRoll]
            goodSubstats[bestRoll] -= 1
            # if you run out of allotted rolls, remove that stat
            if goodSubstats[bestRoll] <= 0:
                goodSubstats.pop(bestRoll)
        return round(rotation(sweaty=sweaty), 2)

    def burst_damage(self, stats, targets=1):
        return self.burst * stats.get_crit_multiplier() * stats.get_attack() * targets *\
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.QDMG]) * self.resMultiplier / 2

    def turret_damage(self, stats, hits):
        return self.skillTurret * stats.get_crit_multiplier() * stats.get_attack() * hits * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * self.resMultiplier / 2

    def skill_cast(self, stats, targets=1):
        return self.skillCast * stats.get_crit_multiplier() * stats.get_attack() * targets *\
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * self.resMultiplier / 2

    def a4_damage(self, stats):
        return self.A4 * stats.get_crit_multiplier() * stats.get_attack() * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * self.resMultiplier / 2

    def c6_damage(self, stats):
        return self.C6 * stats.get_crit_multiplier() * stats.get_attack() * \
               (1 + stats[Attr.DMG] + stats[Attr.ELEMENTDMG] + stats[Attr.EDMG]) * self.resMultiplier / 2

    def ec_damage(self, stats):
        return 2.4 * self.resMultiplier * stats.transformative_multiplier()

    def ol_damage(self, stats):
        return 4 * self.resMultiplier * stats.transformative_multiplier()

    def rotation_sukokomon(self, sweaty=True):
        damage = 0
        if isinstance(self.weapon, bows.AlleyHunter):
            self.weapon.set_stacks(10)
        # use burst
        elif isinstance(self.weapon, bows.PrototypeCrescent) and sweaty:
            self.weapon.set_passive(True)
        elif isinstance(self.weapon, bows.MitternachtsWaltz) and sweaty:
            self.weapon.set_passive(True)
        elif isinstance(self.weapon, bows.PolarStar) and sweaty:
            self.weapon.set_stacks(2)
        currentStats = self.get_stats()

        damage += self.burst_damage(currentStats)
        # average 1 ec proc
        damage += self.ec_damage(currentStats)
        if isinstance(self.weapon, bows.PolarStar):
            # 1 stack from burst
            self.weapon.set_stacks(2 if sweaty else 1)
            currentStats = self.get_stats()
        elif isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()

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
        if isinstance(self.weapon, bows.ElegyForTheEnd) and sweaty:
            self.weapon.set_passive(True)
            currentStats = self.get_stats()
        # average 0.6 ec procs at lowered res
        damage += 0.6*self.ec_damage(currentStats)

        # cast skill after oz duration ends
        if isinstance(self.weapon, bows.PolarStar):
            # It shouldn't be possible to get burst polar stack at this point, at least with c6
            # however you will certainly have one from skill
            self.weapon.set_stacks(2 if sweaty else 2)
        elif isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()
        elif isinstance(self.weapon, bows.PrototypeCrescent) and sweaty:
            self.weapon.set_passive(True)
        currentStats = self.get_stats()
        damage += self.skill_cast(currentStats)
        if isinstance(self.weapon, bows.WindblumeOde):
            self.weapon.skill_cast(True)
            currentStats = self.get_stats()
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

        # use burst
        if isinstance(self.weapon, bows.PrototypeCrescent) and sweaty:
            self.weapon.set_passive(True)
        elif isinstance(self.weapon, bows.MitternachtsWaltz) and sweaty:
            self.weapon.set_passive(True)
        elif isinstance(self.weapon, bows.PolarStar) and sweaty:
            self.weapon.set_stacks(2)
        currentStats = self.get_stats()

        damage += self.burst_damage(currentStats)
        if isinstance(self.weapon, bows.PolarStar):
            # 1 stack from burst
            self.weapon.set_stacks(3 if sweaty else 2)
            currentStats = self.get_stats()
        elif isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += a4procs / 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += c6procs / 2 * self.c6_damage(currentStats)

        # cast skill after oz duration ends
        if isinstance(self.weapon, bows.PolarStar):
            # It shouldn't be possible to get burst polar stack at this point, at least with c6
            # however you will certainly have one from skill
            self.weapon.set_stacks(3 if sweaty else 2)
        elif isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()
        elif isinstance(self.weapon, bows.PrototypeCrescent) and sweaty:
            self.weapon.set_passive(True)
        currentStats = self.get_stats()
        damage += self.skill_cast(currentStats)
        if isinstance(self.weapon, bows.WindblumeOde):
            self.weapon.skill_cast(True)
            currentStats = self.get_stats()
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += a4procs / 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += c6procs / 2 * self.c6_damage(currentStats)
        self.reset()
        return damage

    def rotation_raifish(self, sweaty=False):
        damage = 0
        if isinstance(self.weapon, bows.AlleyHunter):
            self.weapon.set_stacks(10)
        # bennett buffs
        self.buffs[Attr.ATK] = 1119
        self.buffs[Attr.ATKP] = 0.2
        # kazuha buffs
        self.buffs[Attr.ELEMENTDMG] = 0.384
        self.resMultiplier = 1.15
        # raiden buffs
        self.buffs[Attr.QDMG] = 0.18

        # use burst
        if isinstance(self.weapon, bows.PrototypeCrescent) and sweaty:
            self.weapon.set_passive(True)
        elif isinstance(self.weapon, bows.MitternachtsWaltz) and sweaty:
            self.weapon.set_passive(True)
        elif isinstance(self.weapon, bows.PolarStar) and sweaty:
            self.weapon.set_stacks(2)
        """elif isinstance(self.weapon, bows.ElegyForTheEnd):
            # realistically this is only possible second rotation onward and even then the uptime is sus
            self.weapon.set_passive(True)"""
        currentStats = self.get_stats()

        damage += self.burst_damage(currentStats)
        damage += self.ol_damage(currentStats)
        if isinstance(self.weapon, bows.PolarStar):
            # 1 stack from burst
            self.weapon.set_stacks(2 if sweaty else 2)
            currentStats = self.get_stats()
        elif isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += 1 * self.a4_damage(currentStats)
        if self.constellation == 6:
            # assuming 3n3c n1c and a one extra proc somewhere
            damage += 11 * self.c6_damage(currentStats)
        if isinstance(self.weapon, bows.ElegyForTheEnd):
            self.weapon.set_passive(True)
            currentStats = self.get_stats()
        # resummon oz before second rotation but only get 5 hits
        if isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()
        damage += self.skill_cast(currentStats)
        damage += self.turret_damage(currentStats, 5)
        damage += 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            damage += 3 * self.c6_damage(currentStats)

        # second rotation, no fischl e
        damage += self.burst_damage(currentStats)
        if isinstance(self.weapon, bows.SkywardHarp):
            # physical proc
            damage += 0.6 * 1.25 + currentStats.get_crit_multiplier() * currentStats.get_attack()
        damage += self.turret_damage(currentStats, self.turretHits)
        damage += 2 * self.a4_damage(currentStats)
        if self.constellation == 6:
            # assuming 3n3c n1c and a one extra proc somewhere
            damage += 11 * self.c6_damage(currentStats)
        self.reset()
        return damage
