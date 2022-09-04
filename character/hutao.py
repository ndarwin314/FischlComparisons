from character.character_base import*
from weapons import Homa

class HuTao(Character):
    buffID = uuid
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
            self.skillActive= False
            # TODO: hitlag bs
            self.duration = 9 + 2
            self.buffStats = Stats({Attr.ATK:})
            self.skillBuffCreator = lambda t: actions.Buff(self, t, buff.Buff(self.buffStats, t, self.duration, self.buffID), on_field=True)

        def skill(self):
            super().skill()
            self.skillActive = True
            # TODO: hitlag bs
            duration: int = 9 + 2
            self.add_buff()

        def swap_off(self):
            super(HuTao, self).swap_off()
            self.skillActive = False
