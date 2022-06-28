from abc import ABC, abstractmethod
import math

class Summon(ABC):

    def __init__(self, stats, who_summoned, start, duration, rotation):
        self.stats = stats
        self.summoner = who_summoned
        self.endTime = math.ceil(60*(start + duration))
        self.start = start
        self.duration = duration
        self.buffs = []
        self.rotation = rotation

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

    @property
    def time(self):
        return self.rotation.time

