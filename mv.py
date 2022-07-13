class MV:
    def __init__(self, atk_mv=0, def_mv=0, hp_mv=0):
        self.atkMV = atk_mv
        self.defMV = def_mv
        self.hpMV = hp_mv

    def get_base(self, stats):
        return self.atkMV * stats.get_attack() + \
               self.defMV * stats.get_def() +\
               self.hpMV * stats.get_hp()