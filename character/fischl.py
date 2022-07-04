from character.character_base import*
from weapons import AlleyHunter

class Fischl(Character):
    skillTurretBase = 0.888
    skillCastBase = 1.1544
    n1Base = 0.4412
    burstBase = 2.08
    aimBase = 0.4386
    autoBase = [np.array([0.4412, 0.4678, 0.5814, 0.5771, 0.7207])]
    A4 = 0.8
    C6 = 0.3


    class Oz(Summon):
        # i am ignoring hitlag
        def __init__(self, statsRef, who_summoned, start, duration):
            super().__init__(None, who_summoned, start, duration)
            self.mv = who_summoned.skillTurret
            self.lastA4 = start
            self.con = who_summoned.constellation
            self.statsRef = statsRef

        def on_frame(self):
            if (self.rotation.frame - math.ceil(60 * self.start)) % 60 == 0:
                self.rotation.do_damage(self.summoner, self.mv, Element.ELECTRO,
                                        damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)

        def c6(self, time=None):
            self.rotation.do_damage(self.summoner, 0.3, Element.ELECTRO, time=time,
                                    damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)

        def a4(self, character):
            # TODO: make it only apply to electro reactions
            if self.rotation.time > self.lastA4 + 0.5 and self.rotation.onField == self.rotation.characters[character]:
                self.rotation.do_damage(self.summoner, 0.8, Element.ELECTRO,
                                        damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)
                self.lastA4 = self.time

        def summon(self, overwrite=False):
            super().summon()
            self.stats = self.statsRef()
            if self.con >= 6:
                self.rotation.normalAttackHook.append(self.c6)
            if self.con >= 1:
                self.rotation.normalAttackHook.remove(self.summoner.c1)
            self.rotation.reactionHook.append(self.a4)

        def recall(self):
            super().recall()
            if self.con >= 6:
                self.rotation.normalAttackHook.remove(self.c6)
            if self.con >= 1:
                self.rotation.normalAttackHook.append(self.summoner.c1)
            self.rotation.reactionHook.remove(self.a4)

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=6,
                 weapon=AlleyHunter(refinement=1), artifact_set=(SetCount(Set.ATK, 2), SetCount(Set.ATK, 2)),
                 gambler_slots=None):
        super().__init__(Stats({Attr.HPBASE: 9189,
                                Attr.ATKBASE: 244,
                                Attr.DEFBASE: 594,
                                Attr.ATKP: 0.24,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5,
                                Attr.ER: 1}),
                         Element.ELECTRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.SkillFirst, 60)
        self.turretHits = 10 if constellation < 6 else 12
        self.skillTurret = self.skillTurretBase * scalingMultiplier[skill_talent]
        self.skillCast = self.skillCastBase * scalingMultiplier[skill_talent] + (2 if constellation > 1 else 0)
        self.aim = self.aimBase * autoMultiplier[auto_talent]
        # technically c4 is a separate damage instance, but it does not make a big difference
        self.burstMV = self.burstBase * scalingMultiplier[burst_talent] + (2.22 if constellation > 3 else 0)
        self.autoMVS = [self.autoBase[0]*autoMultiplier[auto_talent]]
        self.autoTiming = [[10, 18, 33, 41, 29]]
        # artifacts
        self.artifactStats[Attr.ATKP] += 0.466
        stats = self.get_stats(0)
        if 2 * stats[Attr.CR] > stats[Attr.CD]:
            self.artifactStats[Attr.CD] += 0.622
            self.cdCap -= 2
        else:
            self.artifactStats[Attr.CR] += 0.311
            self.crCap -= 2
        self.artifactStats[Attr.CR] += self.crCap * substatValues[Attr.CR]
        self.artifactStats[Attr.CD] += self.cdCap * substatValues[Attr.CD]
        self.artifactStats[Attr.ATKP] += 2 * substatValues[Attr.ATKP]

    def c1(self):
        self.do_damage(0.22, Element.PHYSICAL, damage_type=DamageType.NORMAL)

    def set_rotation(self, r):
        super().set_rotation(r)
        if self.constellation >= 1:
            self.rotation.normalAttackHook.append(self.c1)

    def normal(sel, hit, **kwargs):
        super().normal(hit)
        # TODO: add c1 loser
        #self.rotation.do_damage(self, self.n1, Element.PHYSICAL, DamageType.NORMAL)

    def charged(self):
        super().charged()
        self.rotation.do_damage(self, self.aim, Element.PHYSICAL, DamageType.CHARGED)

    def skill(self):
        super().skill()
        self.rotation.do_damage(self, self.skillCast, self.element, DamageType.SKILL, time=self.time + 0.6)
        # self.rotation.add_summon(self.Oz(self.skillTurret, self.get_stats(), self, self.time+1.6, self.turretHits))
        self.rotation.add_event(actions.Summon(self, self.time + .6,
                                               self.Oz(lambda :self.get_stats(self.time),
                                                       self, self.time + .6, self.turretHits)))

    def burst(self):
        super().burst()
        self.rotation.do_damage(self, self.burstMV , self.element, DamageType.BURST, time=self.time + 0.24,
                                aoe=True)
        self.rotation.add_event(actions.Summon(self, self.time + .4,
                                               self.Oz(lambda :self.get_stats(self.time),
                                                       self, self.time + .4, self.turretHits)))