from abc import ABC, abstractmethod
import math

class Summon(ABC):

    def __init__(self, stats, who_summoned, start, duration):
        self.stats = stats
        self.summoner = who_summoned
        self.endTime = math.ceil(60*(start + duration))
        self.start = start
        self.duration = duration
        self.buffs = []

    def on_frame(self, rotation):
        pass

    @abstractmethod
    def summon(self, rotation):
        for s in rotation.summons:
            if type(self) == type(s):
                rotation.summons.remove(s)
        rotation.summons.append(self)

    @abstractmethod
    def recall(self, rotation):
        rotation.summons.remove(self)

