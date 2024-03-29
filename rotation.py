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

class Events:
    def __init__(self, action_list, length, rotation):
        self.frame = 0
        self.events = [[] for _ in range(60 * 45)]
        self.actionList = action_list
        self.length = length
        self.rotation = rotation
        for action in action_list:
            self.add_event(action)

    @property
    def time(self):
        return self.frame / 60

    def add_event(self, event):
        try:
            self.events[event.frame].append(event)
        except IndexError:
            pass

    def reset(self):
        self.frame = 0
        self.events = [[] for _ in range(math.ceil((self.length+1) * 60))]
        for action in self.actionList:
            self.add_event(action)

    def execute(self):
        for frame in self.events:
            for summon in self.rotation.summons:
                summon.on_frame()
            for action in frame:
                action.do_action(self.rotation)
            self.frame += 1



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
        self.events = Events(action_list, length, self)
        self.characters = characters
        self.enemyCount = enemy_count
        self.reset()

    @property
    def time(self):
        return self.events.time

    def do_rotation(self):
        if self.logging:
            with open(self.file, "w+") as f:
                f.write("time, damage, mv, attack, em, cr, cd, damage bonus, character, element, reaction, damage type, aoe\n")
        self.events.execute()

    def reset(self):
        self.frame = 0
        self.aura = Aura.NONE
        self.summons = []
        self.damageDict = {char: 0 for char in self.characters}
        self.damageHooks = []
        self.normalAttackHook = []
        self.chargedAttackHook = []
        self.reactionHook = []
        self.swapHooks = []
        self.onField = self.characters[0]
        self.enemies = [enemy.Enemy() for _ in range(self.enemyCount)]
        self.events.reset()
        for char in self.characters:
            char.reset()
            char.set_rotation(self)
            char.weapon.equip(char)

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

    """# TODO: this wasn't a method before and it was fine so idk what is going on
    def recall_summon(self, summon):
        for s in self.summons:
            if type(summon) == type(s):
                s.recall()
        # why is recall summoning?
        summon.summon()"""

    def add_event(self, event):
        self.events.add_event(event)

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
