from character.character_base import*
from weapons import IronSting
import attributes
from buff import Buff

class Kazuha(Character):
    burstCastBase = 2.624
    burstDOTBase = 1.2
    burstInfuseDOTBase = 0.36
    skillPressBase = 1.92
    skillHoldBase = 2.6080
    lowPlungeBase = 1.6363
    highPlungeBase = 2.0439
    buffIDS = {Element.PYRO: uuid(),
               Element.HYDRO: uuid(),
               Element.ELECTRO: uuid(),
               Element.CRYO: uuid()}

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=IronSting(), artifact_set=(SetCount(Set.VV, 4),)):
        super().__init__(Stats({Attr.HPBASE: 13348,
                                Attr.ATKBASE: 297,
                                Attr.DEFBASE: 807,
                                Attr.EM: 115.2,
                                Attr.ER: 1,
                                Attr.CR: 0.05,
                                Attr.CD: 0.5}),
                         Element.ANEMO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)
        # TODO: add stuff cor cons if i care
        self.burstCast = self.burstCastBase * scalingMultiplier[burst_talent]
        self.burstDOT = self.burstDOTBase * scalingMultiplier[burst_talent]
        self.burstInfuseDOT = self.burstInfuseDOTBase * scalingMultiplier[burst_talent]
        self.skillHold = self.skillHoldBase * scalingMultiplier[skill_talent]
        self.skillPress = self.skillPressBase * scalingMultiplier[skill_talent]
        self.lowPlunge = self.lowPlungeBase * scalingMultiplier[auto_talent]
        self.highPlunge = self.highPlungeBase * scalingMultiplier[auto_talent]

        # artifacts stats
        self.artifactStats[Attr.ANEMODMG] -= 0.466
        # TODO: probably make a method to add substats
        self.artifactStats[Attr.EM] += 187 * 3 + 4 * substatValues[Attr.EM]
        self.artifactStats[Attr.ER] += 10 * substatValues[Attr.ER]
        self.artifactStats[Attr.ATKP] += 6 * substatValues[Attr.ATKP]

    def normal(self, hit, **kwargs):
        raise NotImplemented("why")

    def charged(self):
        raise NotImplemented("why")

    def skill(self, **kwargs):
        super().skill()
        # TODO: tap/hold
        infusion = kwargs["infusion"]
        time = self.time + 0.23
        # chiha whatever
        self.rotation.do_damage(self, self.skillPress, self.element, DamageType.SKILL, time, True)
        time += 0.8
        # a1
        self.rotation.do_damage(self, 2, infusion, DamageType.PLUNGE, time, True)
        # plunge
        self.rotation.do_damage(self, self.highPlunge, self.element, DamageType.PLUNGE, time, True)

    def burst(self, **kwargs):
        super().burst()
        element = kwargs["infusion"]
        t = self.time + 93 / 60
        statsRef = lambda : self.get_stats()
        self.rotation.do_damage(self, self.burstCast, self.element, DamageType.BURST, t, True, stats_ref=statsRef)
        t += 1.08
        for i in range(4):
            t += 1.95
            self.rotation.do_damage(self, self.burstDOT, self.element, DamageType.BURST, t, True, stats_ref=statsRef)
            self.rotation.do_damage(self, self.burstInfuseDOT, element, DamageType.BURST, t, True, stats_ref=statsRef)

    def reaction(self, stats, reaction):
        super().reaction(stats, reaction)
        if reaction.is_swirl():
            element = reaction.element()
            dmgBonus = Stats({attributes.elementDict[element]: self.get_stats(self.time)[Attr.EM] * 0.0004})
            self.rotation.add_event(actions.Buff(self, self.time, Buff(dmgBonus, self.time, 8, self.buffIDS[element])))