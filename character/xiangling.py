from character.character_base import*
from weapons import Catch, Kitain

class Xiangling(Character):

    pyronadoBase = np.array([0.72, 0.88, 1.096, 1.12])
    goobaBase = 1.1128
    autoBase = [np.array([0.7726, 0.7742])]

    class Pyronado(Summon):
        def __init__(self, who_summoned, start, stats_ref):
            super().__init__(None, who_summoned, start,  who_summoned.pyronadoDuration)
            self.mv = who_summoned.pyronadoMVS[3]
            self.statsRef = stats_ref
            self.lastHit = start

        def summon(self):
            super().summon()
            self.stats = self.statsRef()

        def recall(self):
            super().recall()

        def on_frame(self):
            if self.time >= self.lastHit + 1.2:
                self.lastHit = self.time
                self.summoner.do_damage(self.mv, Element.PYRO, damage_type=DamageType.BURST,
                                        stats_ref=lambda : self.stats, aoe=True, reaction=Reactions.WEAK, debug=False)
                #self.rotation.add_event(actions.Reaction(self.summoner, self.time + 0.05, Reactions.OVERLOAD))

    class Gooba(Summon):
        shredID = uuid()
        def __init__(self, who_summoned, start, stats_ref):
            super().__init__(None, who_summoned, start, 8)
            self.mv = who_summoned.goobaMV
            self.statsRef = stats_ref
            self.lastHit = start + 0.45

        def summon(self):
            super().summon()
            self.stats = self.statsRef()

        def recall(self):
            super().recall()

        def on_frame(self):
            # TODO: chili
            t = self.time
            if t >= self.lastHit + 1.6:
                self.lastHit = t
                # hack because i dont want to hard code all the overloads and vapes
                # TODO: make this not suck
                self.summoner.do_damage(self.mv, Element.PYRO, damage_type=DamageType.SKILL,
                                        stats_ref=lambda: self.stats, aoe=True, reaction=Reactions.WEAK)
                #self.rotation.add_event(actions.Reaction(self.summoner, t+0.05, Reactions.OVERLOAD))
                if self.summoner.constellation >= 1:
                    self.rotation.add_event(actions.ResShred(self.summoner, t + 1/60, ResShred(Element.PYRO, -0.15, t+6, self.shredID)))


    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=Catch(refinement=5), artifact_set=(SetCount(Set.EMBLEM, 4),)):
        super().__init__(Stats({Attr.HPBASE: 10875,
                                Attr.ATKBASE: 225,
                                Attr.DEFBASE: 669,
                                Attr.EM: 96,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1}),
                         Element.PYRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.BurstFirst, 80)
        self.pyronadoDuration = 10 if constellation <= 4 else 14
        self.pyronadoMVS = self.pyronadoBase * scalingMultiplier[self.burstTalent]
        self.goobaMV = self.goobaBase * scalingMultiplier[self.skillTalent]
        self.autoTiming = [[12, 26]]
        self.autoMVS = [self.autoBase[0] * autoMultiplier[self.autoTalent]]

        erReq = 2.3
        if isinstance(weapon, Kitain):
            erReq -= 0.04 * weapon.refinement + 0.6
            self.artifactStats[Attr.CR] += 0.311
            self.artifactStats[Attr.EM] += 187
            self.crCap -= 2
            erSubs =  int(max(erReq - self.get_stats()[Attr.ER], 0) / substatValues[Attr.ER] + 1)
            if erSubs == 0:
                crSubs = 8 - erSubs // 2
                cdSubs = 20 - crSubs - erSubs
            else:
                crSubs = 8 - erSubs // 2 + 1
                cdSubs = 20 - crSubs -erSubs
            self.add_substat(Attr.CR, crSubs)
            self.add_substat(Attr.CD, cdSubs)
            self.add_substat(Attr.ER, erSubs)

        """elif isinstance(self.weapon, Catch):
            self.artifactStats[Attr.EM] += 187
            # self.artifactStats[Attr.ER] += 0.518
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        else:
            raise ValueError("tell mathy they suck")"""


    def normal(self, hits, **kwargs):
        super(Xiangling, self).normal(hits, **kwargs)

    def charged(self):
        raise NotImplementedError()

    def skill(self):
        t = self.time
        # TODO: chili pepper thing
        self.rotation.add_event(actions.Summon(self, t,
                                               self.Gooba(self, t, lambda: self.get_stats(self.time))))

    def burst(self):
        t = self.time
        t += 0.3
        self.do_damage(self.pyronadoBase[0], self.element, damage_type=DamageType.BURST, time=t, aoe=True)
        #self.rotation.add_event(actions.Reaction(self, t + 0.05, Reactions.OVERLOAD))
        t += 0.25
        self.do_damage(self.pyronadoBase[1], self.element, damage_type=DamageType.BURST, time=t, aoe=True)
        t += 0.38
        self.do_damage(self.pyronadoBase[2], self.element, damage_type=DamageType.BURST, time=t, aoe=True)
        self.rotation.add_event(actions.Summon(self, t,
                                               self.Pyronado(self, t, lambda :self.get_stats(self.time))))