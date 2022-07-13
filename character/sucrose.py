import actions
import attributes
from character.character_base import*
from weapons import TTDS

class Sucrose(Character):
    autoBase = [np.array([0.3346, 0.3062, 0.3845, 0.4792]), np.array([1.2016])]
    autoTiming = [[19, 19, 32, 31]]
    burstBase = np.array([1.48, 0.44])
    skillBase = 2.212
    a1ID = uuid()
    a4ID = uuid()
    c6ID = uuid()

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=TTDS(), artifact_set=(SetCount(Set.VV, 4),)):
        super().__init__(Stats({Attr.HPBASE: 9243,
                                Attr.ATKBASE: 170,
                                Attr.DEFBASE: 703,
                                Attr.ER: 1,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ANEMODMG: 0.24}),
                         Element.ANEMO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.SkillFirst, 80)
        self.burstHits = 4 if self.constellation > 1 else 3
        self.autoMVS = [self.autoBase[0] * scalingMultiplier[self.autoTalent],
                        self.autoBase[1] * scalingMultiplier[self.autoTalent]]
        self.burstMVS = self.burstBase * scalingMultiplier[self.burstTalent]
        self.skillMV = self.skillBase * scalingMultiplier[self.skillTalent]
        self.a4Creator = lambda t: actions.Buff(self, t, buff.Buff(Stats({Attr.EM:self.get_stats()[Attr.EM] / 5}), t, 8, self.a4ID), to_self=False)
        self.a1Creator = lambda t, c: actions.BuffTarget(self, t,
                                                buff.Buff(Stats({Attr.EM: 50}), t, 8, self.a1ID), c)
        self.c6Creator = lambda t, e: actions.Buff(self, t, buff.Buff(Stats({elementDict[e]: 0.2}), t, 10, self.c6ID))
        self.autoTiming = [[19, 19, 32, 31]]
        self.artifactStats[Attr.EM] += 187*3
        self.artifactStats[Attr.ANEMODMG] = 0
        self.add_substat(Attr.EM, 4)
        self.add_substat(Attr.ER, 2)
        self.add_substat(Attr.ATKP, 10)
        self.add_substat(Attr.CR, 4)

    def reaction(self, reaction, **kwargs):
        super().reaction(reaction)
        if reaction.is_swirl():
            # i love gouba swirl
            try:
                bullshit = kwargs["bs"]
            except KeyError:
                bullshit = False
            element = reaction.element()
            if not bullshit:
                for chr in self.rotation.characters:
                    if chr.element == element:
                        self.rotation.add_event( self.a1Creator(self.time, chr))

    def normal(self, hits, **kwargs):
        t = self.time
        for i in range(hits):
            t += self.autoTiming[0][i] / 60
            #print(t)
            self.rotation.do_damage(self, self.autoMVS[0][i], self.element, DamageType.NORMAL, t)
            for hook in self.rotation.normalAttackHook:
                hook()

    def charged(self):
        raise NotImplementedError("literally no one does this")

    def skill(self):
        super(Sucrose, self).skill()
        t = self.time + 0.7
        self.do_damage(self.skillMV, self.element, DamageType.SKILL, aoe=True, time=t)
        # sucrose a4
        # standard dumb bullshit stuff if sucrose's em changes
        self.rotation.add_event(self.a4Creator(t))

    def burst(self, **kwargs):
        super(Sucrose, self).burst()
        element = kwargs["infusion"]
        t = self.time + 67 / 60
        #self.rotation.add_event()
        if self.constellation >= 6:
            self.rotation.add_event(self.c6Creator(t, element))
        for i in range(self.burstHits):
            t += 1.95
            self.rotation.do_damage(self, self.burstMVS[0], self.element, DamageType.BURST, t, True)
            self.rotation.do_damage(self, self.burstMVS[1], element, DamageType.BURST, t, True)
            # standard dumb bullshit stuff if sucrose's em changes

