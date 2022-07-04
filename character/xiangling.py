from character.character_base import*
from weapons import Catch

class Xiangling(Character):

    pyronadoBase = np.array([0.72, 0.88, 1.096, 1.12])
    goobaBase = 1.1128

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
            if self.time > self.lastHit + 1.2:
                self.lastHit = self.time
                self.summoner.do_damage(self.mv, Element.PYRO, damage_type=DamageType.BURST,
                                        stats_ref=lambda : self.stats, aoe=True)

    class Gooba(Summon):
        def __init__(self, who_summoned, start, stats_ref):
            super().__init__(None, who_summoned, start, who_summoned.pyronadoDuration)
            self.mv = who_summoned.goobaMV
            self.statsRef = stats_ref
            self.lastHit = start + 0.5

        def summon(self):
            super().summon()
            self.stats = self.statsRef()

        def recall(self):
            super().recall()

        def on_frame(self):
            if self.time > self.lastHit + 1.5:
                self.lastHit = self.time
                t = DamageType.BURST
                self.summoner.do_damage(self.mv, Element.PYRO, damage_type=DamageType.SKILL,
                                        stats_ref=lambda: self.stats, aoe=True, debug=False)


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


    def normal(self, hits, **kwargs):
        raise NotImplementedError()

    def charged(self):
        raise NotImplementedError()

    def skill(self):
        t = self.time
        self.rotation.add_event(actions.Summon(self, t,
                                               self.Gooba(self, t, lambda: self.get_stats(self.time))))

    def burst(self):
        t = self.time
        t += 0.3
        self.do_damage(self.pyronadoBase[0], self.element, damage_type=DamageType.BURST, time=t, aoe=True)
        t += 0.25
        self.do_damage(self.pyronadoBase[1], self.element, damage_type=DamageType.BURST, time=t, aoe=True)
        t += 0.38
        self.do_damage(self.pyronadoBase[2], self.element, damage_type=DamageType.BURST, time=t, aoe=True)
        self.rotation.add_event(actions.Summon(self, t,
                                               self.Pyronado(self, t, lambda :self.get_stats(self.time))))