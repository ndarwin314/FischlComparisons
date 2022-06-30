from character.character_base import*
from weapons import AlleyFlash
import actions

class Bennett(Character):
    skillBase = 1.376
    n1Base = 0.4455
    burstBase = 2.328
    atkBuffRatio = [0, .56, .602, .644, .7, .742, .784, .84, .896, .952, 1.008, 1.064, 1.12, 1.19]
    autoBase = [np.array([0.4455, 0.4274, 0.5461, 0.5968, 0.719]), np.array([0.559, 0.719])]
    autoTiming = [[12, 20, 31, 55, 49]]
    buffID = uuid()

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=AlleyFlash(), artifact_set=(SetCount(Set.NO, 4),)):
        super().__init__(Stats({Attr.HPBASE: 12397,
                                Attr.ATKBASE: 191,
                                Attr.DEFBASE: 771,
                                Attr.ER: 1.267,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.PYRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.SkillFirst, 60)
        self.skillBase = self.skillBase * scalingMultiplier[skill_talent]
        self.burstBase = self.burstBase * scalingMultiplier[burst_talent]
        self.autoMVS = [self.autoBase[0] * autoMultiplier[auto_talent], self.autoBase[1] * autoMultiplier[auto_talent]]
        self.n1 = self.n1Base * autoMultiplier[auto_talent]
        self.buffValue = (self.atkBuffRatio[self.burstTalent] + (0.2 if constellation >= 1 else 0)) \
                         * self.get_stats(0)[Attr.ATKBASE]
        self.buffStats = Stats({Attr.ATK: self.buffValue})
        if constellation >= 6:
            self.buffStats += Stats({Attr.PYRODMG: 0.15})
        # TODO: fix this to make it more correct
        self.buffCreator = lambda t: actions.Buff(self, t, buff.Buff(self.buffStats, t, 2.1, self.buffID), True)
        self.artifactStats[Attr.ER] += 0.518
        stats = self.get_stats(0)
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        self.artifactStats[Attr.CR] += (self.crCap - 1) * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += (self.cdCap - 1) * substatValues[Attr.CD]
        self.artifactStats[Attr.ER] += 4 * substatValues[Attr.ER]

    def normal(self, hit, **kwargs):
        super().normal(hit)
        self.rotation.do_damage(self, self.n1, Element.PHYSICAL, DamageType.NORMAL)

    def charged(self):
        raise NotImplementedError

    def skill(self):
        super().skill()
        self.rotation.do_damage(self, self.skillBase, self.element, damage_type=DamageType.SKILL,
                                time=self.time + 0.27)

    def burst(self):
        super().burst()
        # TODO maybe: bennett burst in game take several ticks to apply which isn't represented with this currently
        self.rotation.do_damage(self, self.burstBase, self.element, DamageType.BURST, aoe=True,
                                time=self.time + 0.62, stats_ref= lambda : self.get_stats())

        self.rotation.add_event(self.buffCreator(self.time))
        for i in range(13):
            self.rotation.add_event(self.buffCreator(self.time + 0.57 + i))
