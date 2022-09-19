import attributes
from character.character_base import*
from weapons import Homa

class HuTao(Character):
    buffID = uuid()
    teamBuffID = uuid()
    atkIncreaseBase = 0.0384
    normalBase = np.array([0.4689, 0.4825])
    chargedBase = 1.3596
    def __init__(self):
        def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                     weapon=Homa(), artifact_set=(SetCount(Set.NO, 4),)):
            super().__init__(Stats({Attr.HPBASE: 15552,
                                Attr.ATKBASE: 106,
                                Attr.DEFBASE: 876,
                                Attr.ER: 1,
                                Attr.CR: 0.05,
                                Attr.CD: 0.884,
                                Attr.PYRODMG: 0.33}),
                         Element.PYRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.SkillFirst, 60)
            self.atkIncrease = self.atkIncreaseBase * lowElemMultiplier[self.skillTalent]
            self.normalMVS = self.normalBase * physLowMultiplier[self.autoTalent]
            self.chargedMV = self.normalBase * physLowMultiplier[self.autoTalent]

            self.skillActive= False
            # TODO: hitlag bs
            self.duration = 9 + 2
            self.skillActive = False
            self.buffStats = Stats({Attr.ATK: self.atkIncrease*self.get_stats().get_hp()})
            self.skillBuffCreator = lambda t, b: actions.Buff(self, t, buff.Buff(b, t, self.duration, self.buffID), on_field=True)
            self.critStats = Stats({Attr.CR: 0.12})
            self.skillTeamBuffCreator = lambda t:  actions.Buff(self, t, buff.Buff(self.teamBuffStats, t, self.duration, self.teamBuffID), to_self=False)

    def skill(self):
        super().skill()
        self.skillActive = True
        # TODO: hitlag bs
        self.rotation.add_event(self.skillBuffCreator(self.time))
        self.rotation.add_event(self.skillTeamBuffCreator(self.time))

    def swap_off(self):
        super(HuTao, self).swap_off()
        self.skillActive = False
