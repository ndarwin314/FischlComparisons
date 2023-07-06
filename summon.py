from abc import ABC, abstractmethod
from statObject import StatObject
import math

class Summon(StatObject):

    def __init__(self, stats, who_summoned, start, duration):
        super().__init__(stats, who_summoned.rotation)
        self.summoner = who_summoned
        self.endTime = math.ceil(60*(start + duration))
        self.start = start
        self.duration = duration

    def on_frame(self):
        pass

    @abstractmethod
    def summon(self):
        for s in self.rotation.summons:
            if type(self) == type(s):
                self.rotation.summons.remove(s)
        self.rotation.summons.append(self)

    @abstractmethod
    def recall(self):
        self.rotation.summons.remove(self)

    def get_stats(self):
        return self.stats

    def get_parent_stats(self):
        return self.get_parent_stats()