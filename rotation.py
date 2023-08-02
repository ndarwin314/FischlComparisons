import math
from collections.abc import Sequence
from functools import partial
from abc import ABC, abstractmethod
import enemy
import character
import icd
from actions import OtherAction, Damage
from attributes import Aura


class AutoSequence:
    def __init__(self, normal=1, charged=False):
        self.normal = normal
        self.charged = charged

icd0 = icd.ICD(0,1)
class Rotation:

    def __init__(self, action_list, characters, length, enemy_count=1, logging=None):
        self.length = length
        if logging is None:
            self.logging = False
            self.file = None
        else:
            self.logging = True
            self.file = "log/" + logging
        self.actionList = action_list
        self.characters = characters
        self.enemyCount = enemy_count
        self.reset()

    @property
    def time(self):
        return self.frame / 60

    def do_rotation(self):
        if self.logging:
            with open(self.file, "w+") as f:
                f.write("time, damage, mv, attack, em, cr, cd, damage bonus, character, element, reaction, damage type, aoe\n")
        frameEnd = self.length * 60
        for frame in self.events:
            if self.frame >= frameEnd:
                return
            for summon in self.summons:
                if self.frame == summon.endTime:
                    summon.recall()
                summon.on_frame()
            for action in frame:
                action.do_action(self)
            self.frame += 1

    def reset(self):
        self.frame = 0
        self.aura = Aura.NONE
        self.summons = []
        self.damageDict = {char: 0 for char in self.characters}
        self.frame = 0
        self.damageHooks = []
        self.normalAttackHook = []
        self.chargedAttackHook = []
        self.reactionHook = []
        self.swapHooks = []
        self.onField = self.characters[0]
        self.enemies = [enemy.Enemy() for _ in range(self.enemyCount)]
        self.events = [[] for _ in range(60 * 45)]
        for action in self.actionList:
            self.add_event(action)
        for char in self.characters:
            char.reset()
            char.set_rotation(self)

    def char_damage(self, char):
        self.do_rotation()
        damage = self.damageDict[char]
        self.reset()
        return damage

    def do_damage(self, char, mv, element, damage_type, time=None, aoe=False, reaction=None, debug=False, stats_ref=None, icd=None):
        time = self.time if time is None else time
        stats_ref = char.get_stats if stats_ref is None else stats_ref
        icd = icd if icd is not None else icd0
        self.add_event(Damage(char, time, stats_ref, mv, element, damage_type, aoe, reaction, debug, icd))

    def add_summon(self, summon):
        for s in self.summons:
            if type(summon) == type(s):
                s.recall()
        summon.summon()

    # TODO: this wasn't a method before and it was fine so idk what is going on
    def recall_summon(self, summon):
        for s in self.summons:
            if type(summon) == type(s):
                s.recall()
        # why is recall summoning?
        summon.summon()

    def add_event(self, event):
        self.events[math.floor(event.time * 60)].append(event)

    def swap(self, character):
        self.onField.swap_off()
        self.onField = character
        self.onField.swap_on()

    @property
    def damage(self):
        return sum([v for v in self.damageDict.values()])

    @property
    def damage_pretty(self):
        return f"total damage was {round(sum([e.damage for e in self.enemies]), 2)}"
