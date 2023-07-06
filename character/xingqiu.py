from character.character_base import*
from weapons import FavSword


class Raincutter(Summon):
    def __init__(self, who_summoned, start):
        super().__init__(None, who_summoned, start, who_summoned.burstDuration)
        self.mv = who_summoned.burstMVS
        self.lastHit = start - 1
        self.wave = 0
        self.t = 0
        self.total = 0
        if who_summoned.constellation == 6:
            self.cycle = [2, 3, 5]
            self.cycleLength = 3
        else:
            self.cycle = [2, 3]
            self.cycleLength = 2

    def sword_wave(self, time, duration):
        if time + duration > self.lastHit + 1:
            # rn just multiplying mv by the number of hits which is a hack
            self.total += self.cycle[self.wave]
            self.summoner.do_damage(self.mv * self.cycle[self.wave], Element.HYDRO, damage_type=DamageType.BURST,
                                    time=self.time + 0.1, stats_ref=lambda: self.summoner.get_stats())
            self.lastHit = min(time, max(time - duration, self.lastHit + 1))
            self.wave = (self.wave + 1) % self.cycleLength
            self.t += 1
            # c2
            if self.summoner.constellation >= 2:
                self.rotation.add_event(
                    actions.ResShred(self, self.time + 1 / 60, self.summoner.c2Creator(self.lastHit)))

    def summon(self):
        super().summon()
        self.rotation.normalAttackHook.append(self.sword_wave)
        self.summoner.BurstActive = True

    def recall(self):
        super().recall()
        #print(self.t)
        self.rotation.normalAttackHook.remove(self.sword_wave)
        self.summoner.BurstActive = False


class Xingqiu(Character):

    skillBase = np.array([1.68, 1.912])
    autoBase = np.array([0.4661,0.4764]) # dont care about the rest
    burstBase = 0.5427
    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=FavSword(refinement=5), artifact_set=(artifacts.Emblem(4),)):
        super().__init__(Stats({Attr.HPBASE: 10222,
                                Attr.ATKBASE: 202,
                                Attr.DEFBASE: 758,
                                Attr.ATKP: 0.24,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1,
                                Attr.HYDRODMG: 0.2}),
                         Element.HYDRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.BurstFirst, 80, er_req=2.2 if constellation<6 else 1.8)
        self.autoTiming = [[9, 34]]
        self.autoMVS = [self.autoBase * physMultiplier[self.autoTalent]]
        self.skillMVS = self.skillBase * scalingMultiplier[self.skillTalent]
        self.burstMVS = self.burstBase * scalingMultiplier[self.burstTalent]
        self.burstDuration = 15 if self.constellation < 2 else 18
        self.burstActive = False
        if constellation >= 2:
            self.c2id = uuid()
            self.c2Creator = lambda t:ResShred(Element.HYDRO, -0.15, t+4, self.c2id)
        stats = self.get_stats(0)
        if stats[Attr.ER] < 1.5:
            self.artifactStats[Attr.ER] += 0.518
        else:
            self.artifactStats[Attr.ATKP] += 0.466
        stats = self.get_stats(0)
        erSubs = 20 - self.distributedSubs
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        if erSubs < 2:
            self.add_substat(Attr.CR, self.crCap)
            self.add_substat(Attr.CD, self.cdCap)
            self.add_substat(Attr.ATKP, 2 - erSubs)
        else:
            crSubs = self.crCap - erSubs // 2 + 1
            cdSubs = 20 - crSubs - erSubs
            self.add_substat(Attr.CR, crSubs)
            self.add_substat(Attr.CD, cdSubs)


    def skill(self):
        t = self.time
        multiplier = 1.5 if (self.burstActive and self.constellation >=4) else 1
        self.do_damage(self.skillMVS[0] * multiplier, Element.HYDRO, damage_type=DamageType.SKILL, time=t + 0.03)
        self.do_damage(self.skillMVS[1] * multiplier, Element.HYDRO, damage_type=DamageType.SKILL, time=t + 0.45)

    def burst(self):
        self.rotation.add_event(actions.Summon(self, self.time+.2, Raincutter(self, self.time+.2)))


