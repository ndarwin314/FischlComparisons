from abc import ABC, abstractmethod
from statObject import StatObject
from actions import OtherAction
import math

class Summon(StatObject):

    def __init__(self, stats, who_summoned, start, duration):
        super().__init__(stats, who_summoned.rotation)
        self.summoner = who_summoned
        self.endTime = math.ceil(60*(start + duration))
        self.start = start
        self.duration = duration
        self.recallEvent = None

    def on_frame(self):
        pass

    @abstractmethod
    def summon(self):
        for s in self.rotation.summons:
            if type(self) == type(s):
                self.rotation.summons.remove(s)
        self.rotation.summons.append(self)
        self.rotation.add_event(temp:=OtherAction(self.summoner, self.start+self.duration, self.recall))
        self.recallEvent = temp

    @abstractmethod
    def recall(self, *args):
        try:
            self.rotation.summons.remove(self)
            self.rotation.events.events[self.endTime].remove(self.recallEvent)
        except ValueError:
            print(self.time)

    def get_stats(self):
        return self.stats

    def get_parent_stats(self):
        return self.get_parent_stats()