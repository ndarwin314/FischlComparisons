from character.character_base import*
from weapons import TTDS


class Kokomi(Character):


    rippleBase = 1.0919
    autoBase = [np.array([0.6838, 0.6154, 0.9431]), np.array([1.4832])]
    burstBonusBase = np.array([0.1042, 0.0484, 0.0678, 0.071])

    class Jellyfish(Summon):

        def __init__(self, mv, stats_ref, who_summoned, start, con, rotation):
            super().__init__(stats_ref, who_summoned, start, 12.05, rotation)
            self.con = con
            self.mv = mv
            self.statsRef = stats_ref

        def summon(self):
            super().summon()
            if not self.summoner.jellyfishActive:
                self.stats = self.statsRef()
            self.summoner.jellyfishActive = True

        def recall(self):
            super().recall()
            self.summoner.jellyfishActive = False

        def on_frame(self):
            if (self.rotation.frame - math.ceil(60 * self.start)) % 120 == 0:
                mvs = mv.MV(atk_mv=self.mv, hp_mv=self.summoner.burstActive * self.summoner.burstBonusMVS[2])
                self.rotation.do_damage(self.summoner, mvs, Element.HYDRO,
                                        damage_type=DamageType.SKILL, stats_ref=lambda : self.stats)

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=TTDS(), artifact_set=(SetCount(Set.TOM, 4),)):
        super().__init__(Stats({Attr.HPBASE: 13471,
                                Attr.ATKBASE: 234,
                                Attr.DEFBASE: 657,
                                Attr.HYDRODMG: 0.288,
                                Attr.ER: 1,
                                Attr.CR: -95, # kleek
                                Attr.CD: 0.5,
                                Attr.HPP: 0.25
                                }),
                         Element.HYDRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)
        self.autoTiming = [[10, 26, 46], [45]]

        self.rippleMV = self.rippleBase * scalingMultiplier[self.skillTalent]
        self.autoMVS = [self.autoBase[0] * scalingMultiplier[self.autoTalent],
                        self.autoBase[1] * scalingMultiplier[self.autoTalent]]
        self.burstBonusMVS = self.burstBonusBase * scalingMultiplier[self.burstTalent]


        self.burstActive = False

        # artifacts
        self.artifactStats[Attr.ER] += 0.518
        self.artifactStats[Attr.HB] += 0.359
        # TODO: subject to change
        self.artifactStats[Attr.HPP] += 10 * substatValues[Attr.HPP]
        self.artifactStats[Attr.ER] += 2 * substatValues[Attr.ER]
        self.artifactStats[Attr.ATKP] += 8 * substatValues[Attr.ATKP]
        self.jellyfishActive = False

    def swap_off(self):
        super().swap_off()
        self.deactivate_burst()

    def skill(self):
        super().skill()
        self.rotation.add_event(actions.Summon(self, self.time + .6, self.Jellyfish(self.rippleMV, lambda :self.get_stats(self.time),
                                                       self, self.time + .5, self.constellation, self.rotation)))

    def normal(self, hits, **kwargs):
        t = self.time
        # this is scuffed because we dont know if we will get the extra mvs until cast time
        # but then i need to add some conditional check later to see if we actually get the mvs
        # so for now it will be like this
        burstBonus = self.burstActive * (0.15 * self.get_stats()[Attr.HB] + self.burstBonusMVS[1])
        for i in range(hits):
            t += self.autoTiming[0][i] / 60
            mvs = mv.MV(atk_mv=self.autoMVS[0][i], hp_mv=burstBonus)
            self.rotation.do_damage(self, self.autoMVS[0][i], self.element, DamageType.NORMAL, t)
            for hook in self.rotation.normalAttackHook:
                hook()

    def charged(self):
        raise NotImplementedError()

    def burst(self):
        self.burstActive = True
        self.do_damage(mv.MV(hp_mv=self.burstBonusMVS[0]), self.element, damage_type=DamageType.BURST)
        self.rotation.add_event(actions.OtherAction(self, self.time + 11.25, lambda r: self.deactivate_burst()))

    def deactivate_burst(self):
        # TODO: make something like this for raiden
        self.burstActive = False
