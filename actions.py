from abc import ABC, abstractmethod
from attributes import DamageType

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
        rotation.swap(rotation.characters[self.character])


class Summon(Action):
    def __init__(self, character, time, summon):
        super().__init__(character, time)
        self.summon = summon

    def do_action(self, rotation):
        rotation.add_summon(self.summon)


class Recall(Action):
    def __init__(self, character, time, summon):
        super().__init__(character, time)
        self.summon = summon

    def do_action(self, rotation):
        rotation.recall_summon(self.summon)


class Damage(Action):
    def __init__(self, character, time, damage, element, damage_type, aoe=False, is_reaction=False, debug=False):
        super().__init__(character, time)
        self.damage = damage
        self.aoe = aoe
        self.element = element
        self.isReaction = is_reaction
        self.debug = debug
        self.damageType = damage_type

    def do_action(self, rotation):
        """for enemy in self.targets:
            rotation.enemies[enemy].take_damage(self.damage, self.element, rotation)"""
        if self.aoe:
            for enemy in rotation.enemies:
                enemy.take_damage(self.damage, self.element, rotation, self.character, is_reaction=self.isReaction,
                                  debug=self.debug)
        else:
            enemy = rotation.enemies[0]
            enemy.take_damage(self.damage, self.element, rotation, self.character, is_reaction=self.isReaction,
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
    def __init__(self, character, time, hit=1):
        super().__init__(character, time)
        self.hit = hit - 1

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.normal(c.get_stats(rotation.time), self.hit)
        for hook in rotation.normalAttackHook:
            hook()


class Charged(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.charged(c.get_stats(rotation.time), **self.args)


class Skill(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.skill(c.get_stats(rotation.time), **self.args)


class Burst(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.burst(c.get_stats(rotation.time), **self.args)


class Reaction(Action):

    def __init__(self, character, time, reaction):
        super().__init__(character, time)
        self.reaction = reaction

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.reaction(c.get_stats(rotation.time), self.reaction)
        for delegate in rotation.reactionHook:
            delegate(self.character)


class Buff(Action):
    def __init__(self, character, time, buff):
        super().__init__(character, time)
        self.buff = buff

    def do_action(self, rotation):
        for char in rotation.characters:
            char.add_buff(self.buff)