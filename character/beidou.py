from character.character_base import*
from weapons import Akuoumaru

class Beidou(Character):
    class Strombreaker(Summon):
        def __init__(self, stats_ref, who_summoned, start):
            super().__init__(None, who_summoned, start,15.01)
            self.mv = who_summoned.burstMVS[1]
            self.lastHit = start - 1
            self.statsRef = stats_ref

        def on_hit(self):
            if self.time >= self.lastHit + 1:
                aoeMod = 1 if self.rotation.enemyCount == 1 else self.summoner.bounces
                self.summoner.do_damage(self.mv * aoeMod, Element.ELECTRO, damage_type=DamageType.BURST, time=self.time + 0.1)
                self.lastHit = self.time

        def summon(self):
            super().summon()
            self.rotation.add_event(actions.ResShred(self, self.time, ResShred(Element.ELECTRO, -0.15, self.time+15, self.summoner.c6ID)))
            for c in self.rotation.characters:
                c.normalHitHook.append(self.on_hit)
                c.chargedHitHook.append(self.on_hit)

        def recall(self):
            super().recall()
            for c in self.rotation.characters:
                c.normalHitHook.removeremoveappend(self.on_hit)

    autoBase = np.array([0.7112, 0.7086, 0.8832, 0.8652, 0.11214])
    skillBase = np.array([1.216, 1.6])
    burstBase = np.array([1.216, 0.96])
    c6ID = uuid()
    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=Akuoumaru(refinement=5), artifact_set=(artifacts.Emblem(4),)):
        super().__init__(Stats({Attr.HPBASE: 13050,
                                Attr.ATKBASE: 225,
                                Attr.DEFBASE: 648,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1,
                                Attr.ELECTRODMG: 0.24}),
                         Element.HYDRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.SkillFirst, 80, er_req=1.3)
        self.autoTiming = [[23, 66]]
        self.autoMVS = [self.autoBase[0] * physMultiplier[self.autoTalent]]
        self.skillMVS = self.skillBase * scalingMultiplier[self.skillTalent]
        self.burstMVS = self.burstBase * scalingMultiplier[self.burstTalent]
        self.bounces = 3 if self.constellation < 2 else 5

    def normal(self, hits, **kwargs):
        super().normal(hits)

    def skill(self, **kwargs):
        stacks = kwargs["stacks"]
        mv = self.skillMVS[0] + stacks* self.skillMVS[1]
        self.do_damage(mv, Element.ELECTRO, DamageType.SKILL, self.time + 0.4)

    def burst(self):
        self.do_damage(self.burstMVS[0], Element.ELECTRO, DamageType.BURST, self.time + 0.47)
