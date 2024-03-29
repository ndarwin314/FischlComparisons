import artifacts
import attributes
from character.character_base import*
from weapons import AlleyHunter, Twilight
import icd
from collections import Counter

class RemovingCounter(Counter):

    def __setitem__(self, key, value):
        if value == 0:
            del self[key]
        else:
            super().__setitem__(key, value)



electroReactions = {Reactions.ELECTROSWIRL, Reactions.EC, Reactions.SUPERCONDUCT, Reactions.OVERLOAD, Reactions.AGGRAVATE}


class Oz(Summon):
    # i am ignoring hitlag
    def __init__(self, stats_ref, who_summoned, start, duration, icd):
        super().__init__(None, who_summoned, start, duration + 0.01)
        self.mv = who_summoned.skillTurret
        self.lastA4 = start - 1
        self.lastHit = start-0.02
        self.con = who_summoned.constellation
        self.statsRef = stats_ref
        self.a4Count = 0
        self.c6Count = 0
        self.ozCount = 0
        self.icd = icd

    def on_frame(self):
        if self.time >= 1 + self.lastHit:
            self.ozCount += 1
            self.lastHit = self.time
            self.rotation.do_damage(self.summoner, self.mv, Element.ELECTRO,
                                    damage_type=DamageType.SKILL, stats_ref=lambda: self.stats, icd=self.icd)

    def c6(self, time, *args):
        self.c6Count += 1
        self.rotation.do_damage(self.summoner, 0.3, Element.ELECTRO, time=time,
                                damage_type=DamageType.SKILL, stats_ref=lambda: self.stats, icd=self.icd)

    def a4(self, character, reaction):
        if not isinstance(character, int):
            character = self.rotation.characters.index(character)
        if reaction in electroReactions and self.rotation.time >= self.lastA4 + 0.5 and self.rotation.onField == \
                self.rotation.characters[character]:
            self.a4Count += 1
            #print(character, self.time, reaction)
            self.rotation.do_damage(self.summoner, 0.8, Element.ELECTRO,
                                    damage_type=DamageType.SKILL, stats_ref=lambda: self.stats)
            self.lastA4 = self.time

    def summon(self, overwrite=False):
        super().summon()
        self.stats = self.statsRef()
        # print(self.stats)
        if self.con >= 6:
            self.rotation.normalAttackHook.append(self.c6)
        if self.con >= 1:
            self.rotation.normalAttackHook.remove(self.summoner.c1)
        self.rotation.reactionHook.append(self.a4)

    def recall(self, *args):
        super().recall(args)
        if self.con >= 6:
            self.rotation.normalAttackHook.remove(self.c6)
        if self.con >= 1:
            self.rotation.normalAttackHook.append(self.summoner.c1)
        self.rotation.reactionHook.remove(self.a4)




class Fischl(Character):
    skillTurretBase = 0.888
    skillCastBase = 1.1544
    n1Base = 0.4412
    burstBase = 2.08
    aimBase = 0.4386
    autoBase = [np.array([0.4412, 0.4678, 0.5814, 0.5771, 0.7207])]
    A4 = 0.8
    C6 = 0.3


    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=AlleyHunter(refinement=1), artifact_set=(artifacts.Glad(2), artifacts.TF(2)),
                 er_requirement=1, aggravate=False, auto_artis=True):
        super().__init__(Stats({Attr.HPBASE: 9189,
                                Attr.ATKBASE: 244,
                                Attr.DEFBASE: 594,
                                Attr.ATKP: 0.24,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1}),
                         Element.ELECTRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.SkillFirst, 60, er_requirement*(0.93 if constellation==6 else 1))
        self.ozICD = icd.ICD(5, 4)
        self.icdList.append(self.ozICD)

        self.turretHits = 10 if constellation < 6 else 12
        self.skillTurret = self.skillTurretBase * scalingMultiplier[self.skillTalent]
        self.skillCast = self.skillCastBase * scalingMultiplier[self.skillTalent] + (2 if constellation >= 2 else 0)
        self.aim = self.aimBase * physMultiplier[self.autoTalent]
        # technically c4 is a separate damage instance, but it does not make a big difference
        self.burstMV = self.burstBase * scalingMultiplier[self.burstTalent] + (2.22 if constellation >= 4 else 0)
        self.autoMVS = [self.autoBase[0] * physMultiplier[self.autoTalent]]
        self.autoTiming = [[10, 18, 33, 41, 29]]

        self.aggravate = aggravate

        # artifacts
        stats = self.get_stats(0)
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        if auto_artis:
            erSubs = 20 - self.distributedSubs
            self.artifactStats[Attr.ATKP] += 0.466
            if erSubs < 2:
                self.add_substat(Attr.CR, self.crCap)
                self.add_substat(Attr.CD, self.cdCap)
                if aggravate:
                    self.add_substat(Attr.EM, 2 - erSubs)
                else:
                    self.add_substat(Attr.ATKP, 2 - erSubs)
            else:
                crSubs = self.crCap - erSubs // 2 + 1
                cdSubs = 20 - crSubs - erSubs
                self.add_substat(Attr.CR, crSubs)
                self.add_substat(Attr.CD, cdSubs)


    def c1(self, character, *args):
        # TODO: figure out the delay or something, also for a4 and c6
        if character == self:
            self.do_damage(0.22, Element.PHYSICAL, damage_type=DamageType.NORMAL)

    def greedy_optim(self, output=False):
        # goblet and circlet realistically cant be anything other than electro and crit so thats still automatic
        rot = self.rotation
        # choose sands
        self.artifactStats[Attr.ATKP] += 0.466
        if self.aggravate:
            atk_damage = rot.char_damage(self)
            self.artifactStats[Attr.ATKP] -= 0.466
            self.artifactStats[Attr.EM] += 187
            em_damage = rot.char_damage(self)
            if atk_damage > em_damage:
                self.artifactStats[Attr.ATKP] += 0.466
                self.artifactStats[Attr.EM] -= 187
        if self.artifact_set == [artifacts.GT(4)]:
            electro_damage =  rot.char_damage(self)
            self.artifactStats[Attr.ELECTRODMG] -= 0.466
            self.artifactStats[Attr.ATKP] += 0.466
            atk_damage = rot.char_damage(self)
            if electro_damage > atk_damage:
                self.artifactStats[Attr.ELECTRODMG] += 0.466
                self.artifactStats[Attr.ATKP] -= 0.466
            else:
                print("cringe")

        # greedy substat optimization
        substat_limits = RemovingCounter({Attr.CR: self.crCap, Attr.CD: self.cdCap, Attr.ATKP: 10, Attr.EM: 10})
        bestSub = None
        bestDamage = 0
        for i in range(self.distributedSubs):
            for sub in substat_limits.keys():
                self.add_substat(sub)
                damage = rot.char_damage(self)
                self.remove_substat(sub)
                if damage > bestDamage:
                    bestDamage = damage
                    bestSub = sub
            self.add_substat(bestSub)
            substat_limits[bestSub] -= 1
        if output:
            print(f"CR subs: {self.crCap - substat_limits[Attr.CR]}",
              f"CD subs: {self.cdCap - substat_limits[Attr.CD]}",
              f"Atk% subs: {10 - substat_limits[Attr.ATKP]}",
              f"EM subs: {10 - substat_limits[Attr.EM]}", self.weapon, self.artifact_set, sep=", ")
            print(self.get_stats())
            print(bestDamage)


    def set_rotation(self, r):
        super().set_rotation(r)
        if self.constellation >= 1:
            self.rotation.normalAttackHook.append(self.c1)

    def normal(self, hit, **kwargs):
        super().normal(hit, **kwargs)

    def charged(self):
        super().charged()
        self.do_damage(self.aim, Element.PHYSICAL, DamageType.CHARGED)

    def skill(self):
        super().skill()
        self.do_damage(self.skillCast, self.element, DamageType.SKILL, time=self.time + 0.6, aoe=True)
        # self.rotation.add_summon(self.Oz(self.skillTurret, self.get_stats(), self, self.time+1.6, self.turretHits))
        self.rotation.add_event(actions.Summon(self, self.time + .6,
                                               Oz(lambda :self.get_stats(self.time),
                                                       self, self.time + .6, self.turretHits, self.ozICD)))

    def burst(self):
        super().burst()
        self.do_damage(self.burstMV , self.element, DamageType.BURST, time=self.time + 0.24,
                                aoe=True)
        self.rotation.add_event(actions.Summon(self, self.time + .4,
                                               Oz(lambda :self.get_stats(self.time),
                                                       self, self.time + .4, self.turretHits, self.ozICD)))



