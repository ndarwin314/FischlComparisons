from character.character_base import*
from weapons import TTDS

class Kokomi(Character):

    class Jellyfish(Summon):

        def __init__(self, mv, stats_ref, who_summoned, start, duration, con, rotation):
            super().__init__(stats_ref)

        def summon(self, ):
            pass

    def __init__(self, auto_talent=9, skill_talent=9, burst_talent=9, constellation=0,
                 weapon=TTDS(), artifact_set=(SetCount(Set.TOM, 4),)):
        super().__init__(Stats({Attr.HPBASE: 13471,
                                Attr.ATKBASE: 234,
                                Attr.DEFBASE: 657,
                                Attr.HYDRODMG: 0.288,
                                Attr.ER: 1,
                                Attr.CR: -95, # kleek
                                Attr.CD: 0.5
                                }),
                         Element.HYDRO, auto_talent, skill_talent, burst_talent, constellation,
                         weapon, artifact_set, ConType.BurstFirst, 90)