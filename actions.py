from abc import ABC, abstractmethod
from attributes import DamageType, Attr, Reactions

class Action(ABC):
    __slots__ = ["character", "time", "type"]

    def __init__(self, character, time):
        self.character = character
        self.time = time
        # do stuff with kwargs if i decide to

    @abstractmethod
    def do_action(self, rotation):
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

class Recall(Action):
    def __init__(self, character, time, summon):
        super().__init__(character, time)
        self.summon = summon

    def do_action(self, rotation):
        rotation.recall_summon(self.summon)

    def __repr__(self):
        return f"Recalling {self.summon} by {self.character} at {self.time}"


class Damage(Action):
    def __init__(self, character, time, stats_ref, mv, element, damage_type, aoe, reaction, debug):
        super().__init__(character, time)
        self.statsRef = stats_ref
        self.mv = mv
        self.aoe = aoe
        self.element = element
        self.reaction = reaction
        self.debug = debug
        self.damageType = damage_type

    def do_action(self, rotation):
        # TODO: implement def ignore
        stats = self.statsRef()
        """if self.debug:
            print(stats)"""
        if isinstance(self.mv, float) or isinstance(self.mv, int):
            mv = self.mv * stats.get_attack()
        else:
            mv = self.mv.get_base(self.statsRef())

        if self.damageType == DamageType.REACTION:
            multiplier = stats.transformative_multiplier(self.reaction)
            transformative = True
        elif self.damageType == DamageType.CLAM:
            multiplier = 1
            transformative = True
        else:
            multiplier = stats.get_multiplier(self.element, self.damageType, self.character.emblem)
            transformative = False

        match self.reaction:
            case Reactions.WEAK:
                mv *= 1.5 * stats.multiplicative_multiplier()
            case Reactions.STRONG:
                mv *= 1.5 * stats.multiplicative_multiplier()
        damage = mv * multiplier
        if self.aoe:
            for enemy in rotation.enemies:
                enemy.take_damage(damage, self.element, rotation, self.character, is_transformative=transformative,
                                  debug=self.debug)
        else:
            enemy = rotation.enemies[0]
            enemy.take_damage(damage, self.element, rotation, self.character, is_transformative=transformative,
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
        c.reaction(self.reaction, **self.args)
        for delegate in rotation.reactionHook:
            delegate(self.character, self.reaction)

    def __repr__(self):
        return f"{self.character} doing {self.reaction} at {self.time}"

class Buff(Action):
    def __init__(self, character, time, buff, on_field=False, to_self=False):
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