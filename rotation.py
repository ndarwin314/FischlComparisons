import math
from collections.abc import Sequence
from abc import ABC, abstractmethod
import enemy
import character
from actions import OtherAction, Damage


class AutoSequence:
    def __init__(self, normal=1, charged=False):
        self.normal = normal
        self.charged = charged


class Rotation:

    def __init__(self, action_list, characters, enemy_count=1):
        self.characters = characters
        for char in self.characters:
            char.set_rotation(self)
        self.onField = characters[0]
        self.enemies = [enemy.Enemy() for _ in range(enemy_count)]
        # dont ask
        self.enemyCount = enemy_count - 1
        self.summons = []
        self.damageDict = {char: 0 for char in self.characters}
        self.frame = 0
        self.damageHooks = []
        self.normalAttackHook = []
        self.reactionHook = []
        # scuffed
        self.events = [[] for _ in range(60 * 45)]
        for action in action_list:
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
                    s.burstCastHook.append(lambda t: OtherAction(s, t, f))"""
                try:
                    if not isinstance(self.characters[0], character.Raiden):
                        self.characters[0].burstCastHook.append(lambda c: OtherAction(self.characters[0], c.time,
                                                                                       lambda r: char.add_resolve(
                                                                                           self.characters[0].energyCost)))
                except IndexError:
                    pass
                try:
                    if not isinstance(self.characters[1], character.Raiden):
                        self.characters[1].burstCastHook.append(lambda c: OtherAction(self.characters[1], c.time,
                                                                                       lambda r: char.add_resolve(
                                                                                           self.characters[1].energyCost)))
                except IndexError:
                    pass
                try:
                    if not isinstance(self.characters[2], character.Raiden):
                        self.characters[2].burstCastHook.append(lambda c: OtherAction(self.characters[2], c.time,
                                                                                       lambda r: char.add_resolve(
                                                                                           self.characters[2].energyCost)))
                except IndexError:
                    pass
                try:
                    if not isinstance(self.characters[3], character.Raiden):
                        self.characters[3].burstCastHook.append(lambda c: OtherAction(self.characters[3], c.time,
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
                    summon.recall()
                summon.on_frame()
            for action in frame:
                action.do_action(self)
            self.frame += 1
        return damage

    def do_damage(self, char, mv, element, damage_type, time=None, aoe=False, reaction=None, debug=False, stats_ref=None):
        if time is None:
            time = self.time
        if stats_ref is None:
            stats_ref = char.get_stats
        self.add_event(Damage(char, time, stats_ref, mv, element, damage_type, aoe, reaction, debug))

    def add_summon(self, summon):
        for s in self.summons:
            if type(summon) == type(s):
                s.recall()
        summon.summon()

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
