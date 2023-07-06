from character.character_base import*
from weapons import FavoniusWarbow


class Yelan(Character):

    class Dice(Summon):
        def __init__(self, who_summoned, start):
            super().__init__(None, who_summoned, start, who_summoned.burstDuration)
            self.mv = mv.MV(hp_mv=who_summoned.burstMVS)
            self.lastHit = start - 1

        def sword_wave(self, time, duration):
            if time > self.lastHit + 1:
                # rn just multiplying mv by the number of hits which is a hack
                self.summoner.do_damage(self.mv * 3, Element.HYDRO, damage_type=DamageType.BURST, time=self.time + 0.1)
                self.lastHit = min(time, max(time-duration, self.lastHit + 1))


        def summon(self):
            super().summon()
            self.rotation.normalAttackHook.append(self.sword_wave)
            self.summoner.BurstActive = True

        def recall(self):
            super().recall()
            self.rotation.normalAttackHook.remove(self.sword_wave)
            self.summoner.BurstActive = False

    skillBase = 0.2261
    autoBase = np.array([0.4068,0.3904]) # dont care about the rest
    burstBase = np.array([0.0731, 0.0487])
    buffID = uuid()
    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=FavoniusWarbow(refinement=5), artifact_set=(artifacts.Emblem(4),)):
        super().__init__(Stats({Attr.HPBASE: 14450,
                                Attr.ATKBASE: 243,
                                Attr.DEFBASE: 547,
                                Attr.CR: 0.242,
                                Attr.CD: 0.5,
                                Attr.ER: 1,
                                Attr.HPP: 0.18}), #TODO: make yelan a1 dynamic
                         Element.HYDRO, auto_talent, skill_talent, burst_talent,
                         constellation, weapon, artifact_set, ConType.BurstFirst, 70, er_req=(1.5 if isinstance(weapon, FavoniusWarbow) else 1.8)) # something about solo hydro
        self.autoTiming = [[15, 14 ]]
        self.autoMVS = [self.autoBase[0] * physMultiplier[self.autoTalent]]
        self.skillMVS = self.skillBase * scalingMultiplier[self.skillTalent]
        self.burstMVS = self.burstBase * scalingMultiplier[self.burstTalent]
        self.burstDuration = 15
        self.burstActive = False
        self.buffCreator = lambda t, i: actions.Buff(self, t, buff.DirectBuff(Stats({Attr.DMG: 0.01+0.035*i}), t, 1.1, self.buffID), on_field=False)

    def skill(self):
        t = self.time
        # TODO: yeah, get frames
        self.do_damage(self.skillMVS[0] , Element.HYDRO, damage_type=DamageType.SKILL, time=t + 0.03)

    def burst(self):
        t = self.time + 91/60
        self.burstActive = True;
        self.do_damage(self.burstMVS[0], Element.HYDRO, damage_type=DamageType.BURST, time=t)
        self.rotation.add_event(actions.Summon(self, self.time+.2, self.Dice(self, t)))
        for i in range(13):
            self.rotation.add_event(self.buffCreator(self.time + i, i))




