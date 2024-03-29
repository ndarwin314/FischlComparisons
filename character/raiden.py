import icd
from character.character_base import*
from actions import OtherAction
from weapons import Catch, Grass
from buff import DirectPermanentBuff


class NotOz(Summon):
    offset = 30
    buffID = uuid()

    # i am ignoring hitlag
    def __init__(self, stats, who_summoned, start, icd):
        super().__init__(stats, who_summoned, start, 25.28)
        self.mv = who_summoned.skillTurretMV
        self.lastHit = start + 0.9
        self.icd = icd

    def coordinated_attack(self):
        if self.time > self.lastHit + 0.9:
            self.lastHit = self.time
            self.rotation.do_damage(self.summoner, self.mv, Element.ELECTRO, damage_type=DamageType.SKILL,
                                    time=self.time + 0.09, stats_ref=lambda: self.summoner.get_stats(), icd=self.icd)

    def summon(self):
        super().summon()
        self.rotation.damageHooks.append(self.coordinated_attack)
        for char in self.rotation.characters:
            test = DirectPermanentBuff(Stats({Attr.QDMG: 0.003 * char.energyCost}), self.buffID)
            char.add_buff(test)

    def recall(self, *args):
        super().recall(args)
        self.rotation.damageHooks.remove(self.coordinated_attack)
        for char in self.rotation.characters:
            char.remove_buff(DirectPermanentBuff(Stats(), self.buffID))

class Raiden(Character):
    skillcastHookBase = 1.172
    skillTurretBase = 0.42
    autoBase = np.array([0.3965, 0.3973, 0.4988, 0.2898, 0.6545, 0.9959])
    burstBase = 4.0080
    burstBaseBonus = 0.0389
    burstAutoBonus = 0.0073
    autoInfuseBase = np.array([0.4474, 0.4396, 0.5382, 0.3089, 0.3098, 0.7394, 0.616, 0.7436])


    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=Catch(), artifact_set=(artifacts.Emblem(4),)):
        super().__init__(Stats({Attr.HPBASE: 12907,
                                Attr.ATKBASE: 337,
                                Attr.DEFBASE: 789,
                                Attr.ER: 1.32,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.ELECTRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90, er_req=1)
        # TODO: add stuff for cons if i care
        self.skillICD = icd.ICD(2.5, 3)
        self.icdList.append(self.skillICD)

        self.resolve = 0
        self.burstExpiration = 0
        self.autoMVS = self.autoBase * physMultiplier[self.autoTalent]
        self.infusedMVS = self.autoInfuseBase * physHighMultiplier[self.burstTalent]
        self.skillCastMV = self.skillcastHookBase * scalingMultiplier[self.skillTalent]
        self.skillTurretMV = self.skillTurretBase * scalingMultiplier[self.skillTalent]
        self.burstMV = self.burstBase * scalingMultiplier[self.burstTalent]
        self.burstBonusMV = self.burstBaseBonus * scalingMultiplier[self.burstTalent]
        self.infusedBonusMV = self.burstAutoBonus * scalingMultiplier[self.burstTalent]
        # i hate timing
        self.autoTiming = [[12, 20, 22, 41, 44], [80]]
        self.autoTimingBad = [[14, 17, 25, 46, 49], [44]]


        # artifacts
        if isinstance(self.weapon, Grass):
            self.artifactStats[Attr.ER] += 0.518
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        elif isinstance(self.weapon, Catch):
            self.artifactStats[Attr.ATKP] += 0.466
            # self.artifactStats[Attr.ER] += 0.518
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        else:
            self.artifactStats[Attr.ATKP] += 0.466
        self.artifactStats[Attr.CR] += self.crCap * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += self.cdCap * substatValues[Attr.CD]
        self.artifactStats[Attr.ER] += 2 * substatValues[Attr.ER]

    def normal(self, hit, **kwargs):
        charged = kwargs.get("charged")
        if charged is None:
            charged = True
        #super().normal(stats, hit)
        t = self.time
        if self.infusion and self.time > self.burstExpiration:
            self.deactivate_burst()

        if self.infusion:
            timing = self.autoTiming
            mvs = self.infusedMVS + self.resolve * self.infusedBonusMV
            for i in range(hit):
                t += timing[0][i] / 60
                self.do_damage(mvs[i], self.element, DamageType.BURST, time=t, icd=self.normalICD)
                for hook in self.rotation.normalAttackHook:
                    hook(t, timing[0][i] / 60)
            if charged:
                t += timing[1][0] / 60
                self.do_damage(mvs[-2], self.element, DamageType.BURST, time=t, icd=self.normalICD)
                self.do_damage(mvs[-1], self.element, DamageType.BURST, time=t, icd=self.normalICD)
                for hook in self.rotation.chargedAttackHook:
                    hook(t, self.autoTiming[0][i] / 60)
        else:
            timing = self.autoTimingBad
            mvs = self.autoMVS
            for i in range(hit):
                t += timing[0][i] / 60
                self.do_damage(mvs[i], Element.PHYSICAL, DamageType.NORMAL, time=t)
                for hook in self.rotation.normalAttackHook:
                    hook(t)
            if charged:
                t += timing[1][0] / 60
                self.do_damage(mvs[-1], Element.PHYSICAL, DamageType.CHARGED, time=t)
                for hook in self.rotation.chargedAttackHook:
                    hook(t, self.autoTiming[0][i] / 60)


    def charged(self):
        super().charged()
        if self.infusion:
            # this is a hack to add both mvs together since i'm lazy and they are simultaneous
            mv = self.infusedMVS[-1] + self.infusedMVS[-2] + 2 * self.resolve * self.infusedBonusMV
            self.do_damage(mv, self.element, DamageType.BURST)

        else:
            self.do_damage(self.autoMVS[-1], Element.PHYSICAL, DamageType.CHARGED)

    def skill(self):
        super().skill()
        self.do_damage(self.skillCastMV, self.element, damage_type=DamageType.SKILL,
                                time=self.time + 0.85, icd=self.skillICD)
        self.rotation.add_summon(NotOz(None, self, self.time, self.skillICD))

    def burst(self):
        super().burst()
        self.infusion = True
        # 115 frames of startup plus 7 seconds of burst plus hitlag
        # TODO: how much does hitlag add
        self.burstExpiration = self.time + 115 / 60 + 7 + 3
        # stacks from 1
        self.resolve = min(self.resolve + 3 * 2, 60)
        mv = self.burstMV + self.burstBonusMV * self.resolve
        # there is a problem wherein if a burst is used between this being called and the burst hit the resolve won't count
        # but that is impossible in game anyway so idc
        self.do_damage(mv, self.element, DamageType.BURST, self.time + 1.63, aoe=True)
        self.rotation.add_event(actions.OtherAction(self, self.burstExpiration, lambda r: self.deactivate_burst()))

    def add_resolve(self, cost, *args):
        # TODO: change multiplier to be correct for other talent levels
        if self.constellation > 0:
            if 1:
                pass
        self.resolve = min(cost * 0.19 + self.resolve, 60)

    def get_stats(self, time=None):
        stats = super().get_stats(time)
        a4 = Stats({elementDict[self.element]: (stats[Attr.ER] - 1) * 0.4})
        stats += a4
        return stats

    def swap_off(self):
        self.deactivate_burst()

    def deactivate_burst(self):
        self.infusion = False
        self.resolve = 0

    def set_rotation(self, r):
        super().set_rotation(r)
        for char in r.characters:
            f = partial(self.add_resolve, char.energyCost)
            char.burstCastHook.append(lambda c: OtherAction(self, self.time, f))

    def reset(self):
        super().reset()
        self.resolve = 0