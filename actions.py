from abc import ABC, abstractmethod
from attributes import DamageType, Attr, Reactions, Element, Aura
from icd import ICD
import logging

class Action(ABC):
    __slots__ = ["character", "time", "type"]

    def __init__(self, character, time):
        self.character: "Character" = character
        self.time: int = time
        try:
            self.logging = character.rotation.logging
        except AttributeError:
            self.logging = False
        # do stuff with kwargs if i decide to

    @abstractmethod
    def do_action(self, rotation: "Rotation") -> None:
        rotation.characters[self.character].remove_expired_buffs()


class OtherAction(Action):
    def __init__(self, character, time, method):
        super().__init__(character, time)
        self.action = method

    def do_action(self, rotation):
        self.action(rotation)


class Swap(Action):
    def __init__(self, character, time):
        super().__init__(character, time)

    def do_action(self, rotation):
        #print(rotation.characters[self.character], self.time)
        c = rotation.characters[self.character]
        for hook in rotation.swapHooks:
            hook(c)
        rotation.swap(rotation.characters[self.character])

    def __repr__(self):
        return f"Swapping to {self.character} at {self.time}"


class Summon(Action):
    def __init__(self, character, time, summon):
        super().__init__(character, time)
        self.summon = summon

    def do_action(self, rotation):
        rotation.add_summon(self.summon)

    def __repr__(self):
        return f"Summoning {self.summon} by {self.character} at {self.time}"

"""class Recall(Action):
    def __init__(self, character, time, summon):
        super().__init__(character, time)
        self.summon = summon

    def do_action(self, rotation):
        rotation.recall_summon(self.summon)

    def __repr__(self):
        return f"Recalling {self.summon} by {self.character} at {self.time}"""

class SetAura(Action):
    def __init__(self, character: "Character", time: int, aura: Aura):
        super().__init__(character, time)
        self.aura : Aura = aura

    def do_action(self, rotation: "Rotation") -> None:
        rotation.aura = self.aura


class Damage(Action):
    def __init__(self, character, time, stats_ref, mv, element, damage_type, aoe, reaction, debug, icd):
        super().__init__(character, time)
        self.statsRef = stats_ref
        self.mv: "mv.MV" = mv
        self.aoe: bool = aoe
        self.element: Element = element
        self.reaction: Reactions = reaction
        self.debug: bool = debug
        self.damageType: DamageType = damage_type
        self.icd: ICD = icd

    def do_action(self, rotation: "Rotation") -> None:
        # TODO: implement def ignore
        stats = self.statsRef()
        for b in self.character.directBuffs:
            stats += b.buff()
        element_applied = self.icd.applied_element(rotation.time) and self.element != Element.PHYSICAL
        atk = stats.get_attack()
        em = stats[Attr.EM]
        if isinstance(self.mv, float) or isinstance(self.mv, int):
            mv_log = self.mv
            mv = self.mv * atk
        else:
            mv = self.mv.get_base(self.statsRef())
            mv_log = mv

        if self.damageType == DamageType.REACTION:
            multiplier = stats.transformative_multiplier(self.reaction)
            transformative = True
        elif self.damageType == DamageType.CLAM:
            multiplier = 1
            transformative = True
        else:
            if self.debug:
               t = 1
            multiplier = stats.get_multiplier(self.element, self.damageType, self.character.emblem)
            transformative = False


        # TODO: expand this
        # TODO: this code is so fucking ugly
        reaction: Reactions = self.reaction
        if element_applied:
            reactions: list[Reactions] = []
            match rotation.aura:
                case Aura.PYRO:
                    pass
                case Aura.HYDRO:
                    match self.element:
                        case Element.PYRO:
                            mv *= 1.5 * stats.multiplicative_multiplier()
                            reaction = Reactions.REVERSEVAPE
                case Aura.ELECTRO:
                    # TODO: add some quicken bs
                    match self.element:
                        case Element.ANEMO:
                            self.character.reaction(Reactions.ELECTROSWIRL)
                            reactions.append(Reactions.ELECTROSWIRL)
                        case Element.PYRO:
                            self.character.reaction(Reactions.OVERLOAD)
                            reactions.append(Reactions.OVERLOAD)
                case Aura.CRYO:
                    pass
                case Aura.EC:
                    match self.element:
                        case Element.ANEMO:
                            #self.character.reaction(Reactions.HYDROSWIRL)
                            #reactions.append(Reactions.HYDROSWIRL)
                            self.character.reaction(Reactions.ELECTROSWIRL)
                            reactions.append(Reactions.ELECTROSWIRL)
                        case Element.PYRO:
                            self.character.reaction(Reactions.OVERLOAD)
                            reactions.append(Reactions.OVERLOAD)
                            mv *= 1.5 * stats.multiplicative_multiplier()
                            reaction = Reactions.REVERSEVAPE
                case Aura.QUICKEN:
                    match self.element:
                        case Element.ELECTRO:
                            m = self.character.get_stats()[Attr.EM]
                            mv += 1.15 * 1447 * (1 + 5 * em / (1200 + em) + stats[Attr.AGGRAVATEBONUS])
                            reactions.append(Reactions.AGGRAVATE)
                            reaction = Reactions.AGGRAVATE
                        case Element.DENDRO:
                            em = self.character.get_stats()[Attr.EM]
                            mv += 1.25 * 1447 * (1 + 5 * em / (1200 + em))
                            reactions.append(Reactions.SPREAD)
                            reaction = Reactions.SPREAD
                        case Element.ANEMO:
                            self.character.reaction(Reactions.ELECTROSWIRL)
                            reactions.append(Reactions.ELECTROSWIRL)
                case Aura.NONE:
                    match self.reaction:
                        case Reactions.WEAK:
                            mv *= 1.5 * stats.multiplicative_multiplier()
                            reaction = Reactions.REVERSEVAPE
                        case Reactions.STRONG:
                            mv *= 2 * stats.multiplicative_multiplier()
                            reaction = Reactions.FORWARDVAPE
                        case Reactions.AGGRAVATE:
                            em = self.character.get_stats()
                            mv += 1.15 * 1447 * (1 + 5 * em / (1200 + em) + stats[Attr.AGGRAVATEBONUS])
                            reactions.append(Reactions.AGGRAVATE)
            for r in reactions:
                for delegate in rotation.reactionHook:
                    delegate(self.character, r)
                for delegate in self.character.reactionHook:
                    delegate(self.character, r)

        damage = mv * multiplier
        if self.aoe:
            for enemy in rotation.enemies:
                damage = enemy.take_damage(damage, self.element, rotation, self.character, is_transformative=transformative,
                                  debug=self.debug)
        else:
            enemy = rotation.enemies[0]
            damage = enemy.take_damage(damage, self.element, rotation, self.character, is_transformative=transformative,
                              debug=self.debug)
        for hook in rotation.damageHooks:
            hook()
        for hook in self.character.damageHook:
            hook(self.character)
        match self.damageType:
            case DamageType.SKILL:
                for hook in self.character.skillHitHook:
                    hook(self.character)
            case DamageType.NORMAL:
                for hook in self.character.normalHitHook:
                    hook(self.character)
            case DamageType.CHARGED:
                for hook in self.character.chargedHitHook:
                    hook(self.character)
            case DamageType.BURST:
                for hook in self.character.burstHitHook:
                    hook(self.character)
        if self.logging:
            with open(rotation.file, "a") as f:
                f.write(f"{self.time:.3f}, {damage:.3f}, {mv_log:.3f}, {atk:.3f}, {em:.3f}, {stats[Attr.CR]:.3f}, {stats[Attr.CD]:.3f}," \
                        f"{stats.get_DMG(self.element, self.damageType, self.character.emblem):.3f}," \
                        f"{self.character}, {self.element}, {reaction}, {self.damageType}, {self.aoe}\n")

    def __repr__(self):
        return f"{self.character} with mv {round(self.mv,2)} at {self.time}"


"""class Auto(Action):
    def __init__(self, character, time, sequence=None):
        super().__init__(character, time)
        if sequence is None:
            self.sequence = Sequence(1, False)
        else:
            self.sequence = sequence

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        # TODO
        time = rotation.time
        for i in range(self.sequence - 1):"""


class Normal(Action):
    def __init__(self, character, time, hit=1, **kwargs):
        super().__init__(character, time)
        self.hit = hit
        self.kwargs = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.normal( self.hit, **self.kwargs)
        """for hook in rotation.normalAttackHook:
            hook()"""

    def __repr__(self):
        return f"{self.character} normal attacking at {self.time}"


class Charged(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.charged(**self.args)

    def __repr__(self):
        return f"{self.character} charged attacking at {self.time}"

class Skill(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.skill(**self.args)

    def __repr__(self):
        return f"{self.character} casting skill at {self.time}"


class Burst(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.burst(**self.args)

    def __repr__(self):
        return f"{self.character} casting burst at {self.time}"


class Reaction(Action):

    def __init__(self, character, time, reaction, vape=False, **kwargs):
        super().__init__(character, time)
        self.reaction = reaction
        self.args = kwargs
        self.vape = vape

    def do_action(self, rotation):
        super().do_action(rotation)
        if isinstance(self.character, int):
            c = rotation.characters[self.character]
        else:
            c = self.character
        c.reaction(self.reaction)
        for delegate in rotation.reactionHook:
            delegate(self.character, self.reaction)

    def __repr__(self):
        return f"{self.character} doing {self.reaction} at {self.time}"

class Buff(Action):
    def __init__(self, character: "Character", time: int, buff: "buff.Buff", on_field=False, to_self=False):
        super().__init__(character, time)
        self.buff = buff
        self.onField = on_field
        self.toSelf = to_self

    def do_action(self, rotation):
        if self.onField:
            rotation.onField.add_buff(self.buff)
        else:
            for char in rotation.characters:
                if self.toSelf and char == self.character:
                    continue
                char.add_buff(self.buff)

    def __repr__(self):
        return f"{self.character} buffing {self.buff} at {self.time}"

class BuffTarget(Buff):
    def __init__(self, character, time, buff, target):
        super().__init__(character, time, buff, False, False)
        self.target = target

    def do_action(self, rotation):
        self.target.add_buff(self.buff)

    def __repr__(self):
        return f"{self.character} buffing {self.buff} at {self.time}"

class ResShred(Action):
    def __init__(self, character, time, res_shred):
        super().__init__(character, time)
        self.resShred = res_shred

    def do_action(self, rotation):
        for e in rotation.enemies:
            e.add_shred(self.resShred)

class Healing(Action):
    def __init__(self, character, time, percent, flat, stats_ref=None):
        super().__init__(character, time)
        self.percent = percent
        self.flat = flat
        self.statsRef = character.get_stats if stats_ref is None else stats_ref

    def do_action(self, rotation):
        stats = self.statsRef()
        healing = (stats.get_hp() * self.percent + self.flat) * (1 + stats[Attr.HB])
        for hook in self.character.healingHook:
            hook(self.character, healing)