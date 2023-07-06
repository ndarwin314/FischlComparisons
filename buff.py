from abc import ABC, abstractmethod
from attributes import Stats

class GenericBuff(ABC):
    def __init__(self, buff, uuid):
        self._buff = buff
        self.id = uuid

    def __eq__(self, other):
        return self.id == other.id

    def buff(self):
        return self._buff

    @abstractmethod
    def is_expired(self, rotation):
        pass

    @abstractmethod
    def __add__(self, other):
        pass

    def __repr__(self):
        return f"Buff {self._buff}"

class Buff(GenericBuff):

    def __init__(self, buff: Stats, start: int, duration: int, uuid: int):
        super().__init__(buff, uuid)
        self.expiration = duration + start

    def is_expired(self, rotation):
        return self.expiration < rotation.time

    def __add__(self, other):
        if self.expiration > other.expiration:
            return self
        else:
            return other

    def __repr__(self):
        return f"Buff {self._buff} expiring at {self.expiration}"

    def buff(self):
        return self._buff

class PermanentBuff(GenericBuff):
    def __init__(self, buff, uuid):
        super().__init__(buff, uuid)

    def is_expired(self, rotation):
        return False

    def __add__(self, other):
        return self

    def buff(self):
        return self._buff

class StackableBuff(GenericBuff):
    def __add__(self, other):
        self.stacks = sorted(self.stacks + other.stacks, key=lambda pair: -pair[1])[0:self.maxStacks]
        return self

    def __init__(self, buff, maxStacks, start, duration, uuid):
        # TODO: add something for an extra buff at max stacks
        super().__init__(buff, uuid)
        self.stacks = [(buff, start+duration)]
        self.maxStacks = maxStacks

    def is_expired(self, rotation):
        self.stacks = [stack for stack in self.stacks if stack[1] > rotation.time]
        return len(self.stacks) == 0

    def buff(self):
        return sum([_[0] for _ in self.stacks], start=Stats())

class DirectGenericBuff(GenericBuff, ABC):
    pass

class DirectBuff(DirectGenericBuff, Buff):
    pass

class DirectPermanentBuff(DirectGenericBuff, PermanentBuff):
    pass
