class ICD:
    def __init__(self, time: float, hits: int):
        self.lastHitTime = -10
        self.hitCounter = -1
        self.icdDuration = time
        self.icdHits = hits

    def applied_element(self, time: int) -> bool:
        self.hitCounter = (self.hitCounter + 1) % self.icdHits
        if self.hitCounter==0 or (time - self.lastHitTime) > self.icdDuration:
            self.lastHitTime = time
            return True
        return False

class WTF(ICD):
    def __init__(self):
        super(WTF, self).__init__(0,0)

    def applied_element(self, time: int) -> bool:
        return False


class Creator:
    def __init__(self, id :int, time: int=0, hits: int=0):
        self.id = id
        self.cd = time
        self.hitPity = hits

    def create(self):
        return ICD(self.cd, self.hitPity)
