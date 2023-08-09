import attr.setters
import numpy as np

from character.character_base import*
import icd
from weapons import LionsRoar
from functools import partial

class Keqing(Character):
    autoBase = [np.array([0.41, 0.41, 0.544, 0.315, 0.344, .67]), np.array([.768, .86])]
    skillBase = np.array([0.504, 1.68, .84])
    burstBase = np.array([0.88, 0.24, 1.89])

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=LionsRoar(refinement=5), artifact_set=(artifacts.TF(4)),
                 er_requirement=1):
        super().__init__(Stats({Attr.HPBASE: 131039,
                                Attr.ATKBASE: 323,
                                Attr.DEFBASE: 799,
                                Attr.CR: 0.05,
                                Attr.CD: 0.884,
                                Attr.ER: 1}),
                         Element.ELECTRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.BurstFirst, 40, er_requirement)
        self.normalMVS = self.autoBase[0] * physMultiplier[self.autoTalent]
        self.chargedMVS = self.autoBase[1] * physMultiplier[self.autoTalent]
        self.skillMVS = self.skillBase * scalingMultiplier[self.skillTalent]
        self.burstMVS = self.burstBase * scalingMultiplier[self.burstTalent]
        #TODO figure out how hitmark actually works
        self.autoTiming = [[21,22,35,37,0,66],[42,0]]

        self.infusionExpiration = 0
        self.stiletto = False

        self.burstICD = icd.ICD(2.5, 3)
        self.icdList.append(self.burstICD)

        self.a4id = uuid()

        self.artifactStats += 0.311
        self.crCap -= 2
        self.add_substat(Attr.CR, self.crCap)
        self.add_substat(Attr.CD, self.cdCap)
        self.add_substat(Attr.ATKP, 2)

    def normal(self, hits, **kwargs):
        if hits >= 3:
            hits += 1
        super().normal(hits, **kwargs)

    # the exploding thing on CA is cringe so i'm not going to implement it
    def skill(self):
        super().skill()
        time = self.time
        if self.stiletto:
            self.do_damage(self.skillMVS[0], Element.ELECTRO, DamageType.SKILL, time=time+24/60, aoe=True)
        else:
            self.infusion = True
            # yada yada hitlag
            self.do_damage(self.skillMVS[1], Element.ELECTRO, DamageType.SKILL, time=time + 25 / 60, aoe=True)
            self.infusionExpiration = time + 5 + 25/60
            self.rotation.add_event(actions.OtherAction(self, self.infusionExpiration, partial(self.end_infusion())))
        self.stiletto = not self.stiletto
        
    def burst(self):
        super().burst()
        time = self.time
        self.rotation.add_event(buff.Buff(Stats({Attr.CR: 0.15, Attr.ER: 0.15}), time, 8, self.a4id))
        time += 56/60
        self.do_damage(self.burstMVS[0], self.element, DamageType.BURST, time, True, icd=self.burstICD)
        for i in range(8):
            # this is approximate but is good enough for me, also goes for below
            time += 15/60
            self.do_damage(self.burstMVS[1], self.element, DamageType.BURST, time, True, icd=self.burstICD)
        time += 36/60
        self.do_damage(self.burstMVS[2], self.element, DamageType.BURST, time, True, icd=self.burstICD)
