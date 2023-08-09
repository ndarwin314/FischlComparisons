from character.character_base import*
from weapons import FavoniusWarbow

class Collei(Character):
    skillBase = 1.512
    burstBase = np.array([2.0182, 0.4325])
    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=FavoniusWarbow(refinement=5), artifact_set=(artifacts.Instructor(4),)):
        super().__init__(Stats({Attr.HPBASE: 9787,
                                Attr.ATKBASE: 199,
                                Attr.DEFBASE: 600,
                                Attr.ATKP: 0.24,
                                Attr.ER: 1,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.DENDRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 60, er_req=1.6)
        self.skillMV = Collei.skillBase * scalingMultiplier[self.skillTalent]
        self.burstMV = Collei.burstBase * scalingMultiplier[self.burstTalent]
        self.burstICD = icd.ICD(3, 6)
        self.icdList.append(self.burstICD)
        self.artifactStats[Attr.ATKP] += 0.466
        self.artifactStats[Attr.CR] += 0.311
        self.add_substat(Attr.CR, self.crCap)
        self.add_substat(Attr.CD, self.cdCap)
        
    def normal(self, hits, **kwargs):
        super(Collei, self).normal(hits, **kwargs)

    def charged(self):
        super(Collei, self).charged()

    def skill(self):
        super(Collei, self).skill()
        # TODO: make this good
        self.do_damage(self.skillMV, self.element, DamageType.SKILL, self.time+0.5)
        self.do_damage(self.skillMV, self.element, DamageType.SKILL, self.time + 3.5)

    def burst(self):
        super(Collei, self).burst()
        t = self.time + 0.617
        self.do_damage(self.burstMV[0], self.element, DamageType.BURST, t, icd=self.burstICD)
        # TODO: this is assuming always 9 second rot with .5 second between hits
        for i in range(18):
            t += 0.5
            self.do_damage(self.burstMV[1], self.element, DamageType.BURST, t,  icd=self.burstICD)