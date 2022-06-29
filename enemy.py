import attributes
from attributes import Element
from functools import cache

class ResShred:
    def __init__(self, element, res, expiration, id):
        self.element = element
        self.expiration = expiration
        self.id = id
        self.res = res

    def is_expired(self, rotation):
        return rotation.time > self.expiration

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{self.element} shred of {self.res} expiring at {self.expiration}"

class Enemy:

    def __init__(self):
        self.damage = 0
        # assuming level 100 enemy and 90 character
        self.defMultiplier = 19/39
        self.resistances = {element: 0.1 for element in Element}
        self.resShred = {element: list() for element in Element}

    def take_damage(self, incoming, element, rotation, character, is_reaction=False, debug=False):
        self.resShred[element] = [s for s in self.resShred[element] if not s.is_expired(rotation)]
        shred = self.resShred[element]
        res = self.resistances[element] + sum([s.res for s in shred])
        multiplier = self.res_multiplier(res)
        if not is_reaction:
            multiplier *= self.defMultiplier
        if debug:
            print(round(multiplier * incoming, 2), round(rotation.time, 2))
        damage = multiplier * incoming
        rotation.damageDict[character] += damage
        self.damage += damage

    def reset(self):
        self.damage = 0
        # assuming level 100 enemy and 90 character
        self.defMultiplier = 19 / 39
        self.resistances = {element: 0.1 for element in Element}
        self.resShred = {element: list() for element in Element}

    @staticmethod
    @cache
    def res_multiplier(res):
        if res > 0.75:
            return 1/(4*res + 1)
        elif res >= 0:
            return 1 - res
        else:
            return 1 - res/2

    def add_shred(self, res_shred):
        if res_shred in self.resShred[res_shred.element]:
            self.resShred[res_shred.element].remove(res_shred)
        self.resShred[res_shred.element].append(res_shred)
