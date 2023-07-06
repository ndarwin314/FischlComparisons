from abc import ABC, abstractmethod
import math

class StatObject(ABC):

    def __init__(self, stats, rotation):
        self.stats = stats
        self.buffs = []
        self.rotation = rotation

    @property
    def time(self):
        return self.rotation.time

    @abstractmethod
    def get_stats(self):
        pass

    @abstractmethod
    def get_parent_stats(self):
        pass