import math
from collections.abc import Sequence
from abc import ABC, abstractmethod
from enum import Enum, auto
import numpy as np
import enemy
import buff
from attributes import DamageType
import character


class AutoSequence:
    def __init__(self, normal=1, charged=False):
        self.normal = normal
        self.charged = charged


class Action(ABC):
    __slots__ = ["character", "time", "type"]

    def __init__(self, character, time):
        self.character = character
        self.time = time
        # do stuff with kwargs if i decide to

    @abstractmethod
    def do_action(self, rotation):
        rotation.characters[self.character].remove_expired_buffs(rotation)


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
            hook(rotation)
        match self.damageType:
            case DamageType.SKILL:
                for hook in self.character.skillHit:
                    hook(rotation, self.character)


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
        c.normal(c.get_stats(), rotation, self.hit)
        for hook in rotation.normalAttackHook:
            hook(rotation)


class Charged(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.charged(c.get_stats(), rotation, **self.args)


class Skill(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.skill(c.get_stats(), rotation, **self.args)


class Burst(Action):
    def __init__(self, character, time, **kwargs):
        super().__init__(character, time)
        self.args = kwargs

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.burst(c.get_stats(), rotation, **self.args)


class Reaction(Action):

    def __init__(self, character, time, reaction):
        super().__init__(character, time)
        self.reaction = reaction

    def do_action(self, rotation):
        super().do_action(rotation)
        c = rotation.characters[self.character]
        c.reaction(c.get_stats(), rotation, self.reaction)
        for delegate in rotation.reactionHook:
            delegate(rotation, self.character)


class Buff(Action):
    def __init__(self, character, time, buff):
        super().__init__(character, time)
        self.buff = buff

    def do_action(self, rotation):
        for char in rotation.characters:
            char.add_buff(self.buff)


class Rotation:

    def __init__(self, actionList, characters, enemyCount=1):
        self.characters = characters
        self.onField = characters[0]
        self.enemies = [enemy.Enemy() for _ in range(enemyCount)]
        # dont ask
        self.enemyCount = enemyCount - 1
        self.summons = []
        self.damageDict = {char: 0 for char in self.characters}
        self.frame = 0
        self.damageHooks = []
        self.normalAttackHook = []
        self.reactionHook = []
        # scuffed
        self.events = [[] for _ in range(60 * 45)]
        for action in actionList:
            self.add_event(action)
        # terrible code
        for i, char in enumerate(self.characters):
            if isinstance(char, character.Raiden):
                # there is some bullshit going on with the lambda functions not binding until after the loop ends
                # which results in the unintended behavior that all characters add resolve of the last character
                # so i'm going to hardcode it to fix it
                """costs = []
                for char2 in self.characters:
                    costs.append(char2.energyCost)
                for j in range(len(self.characters)):
                    s = self.characters[j]
                    f = lambda r: char.add_resolve(costs[j])
                    s.burstActivated.append(lambda t: OtherAction(s, t, f))"""
                try:
                    self.characters[0].burstActivated.append(lambda t: OtherAction(self.characters[0], t,
                                                                                   lambda r: char.add_resolve(
                                                                                       self.characters[0].energyCost)))
                except IndexError:
                    pass
                try:
                    self.characters[1].burstActivated.append(lambda t: OtherAction(self.characters[1], t,
                                                                                   lambda r: char.add_resolve(
                                                                                       self.characters[1].energyCost)))
                except IndexError:
                    pass
                try:
                    self.characters[2].burstActivated.append(lambda t: OtherAction(self.characters[2], t,
                                                                                   lambda r: char.add_resolve(
                                                                                       self.characters[2].energyCost)))
                except IndexError:
                    pass
                try:
                    self.characters[3].burstActivated.append(lambda t: OtherAction(self.characters[3], t,
                                                                                   lambda r: char.add_resolve(
                                                                                       self.characters[3].energyCost)))
                except IndexError:
                    pass
                break

    @property
    def time(self):
        return self.frame / 60

    def do_rotation(self):
        damage = 4 * [0]
        for frame in self.events:
            for summon in self.summons:
                if self.frame == summon.endTime:
                    summon.recall(self)
                summon.on_frame(self)
            for action in frame:
                action.do_action(self)
            self.frame += 1
        return damage

    def do_damage(self, char, damage, element, damage_type, time=None, aoe=False, is_reaction=False, debug=False):
        if time is None:
            time = self.time
        self.add_event(Damage(char, time, damage, element, damage_type, aoe, is_reaction, debug))

    def add_summon(self, summon):
        for s in self.summons:
            if type(summon) == type(s):
                s.recall(self)
        summon.summon(self)

    def add_event(self, event):
        self.events[math.floor(event.time * 60)].append(event)

    def swap(self, character):
        self.onField = character

    @property
    def damage(self):
        return sum([e.damage for e in self.enemies])

    @property
    def damage_pretty(self):
        return f"total damage was {round(sum([e.damage for e in self.enemies]), 2)}"
