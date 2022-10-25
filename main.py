import csv
import time
from multiprocessing import Pool

import artifacts
from artifacts import Set, SetCount
from rotation import *
import character
from weapons import *
from helper import *
from action_lists import RaiFish, Sukokomon, aggravateFish, Test
import actions




weapons = [PolarStar, Water, Hunter, SkywardHarp, ThunderingPulse, TheViridescentHunt, AmosBow, AlleyHunter, PrototypeCrescent,
               Twilight, MouunsMoon, ElegyForTheEnd, Rust, TheStringless, Hamayumi, WindblumeOde, SacrificialBow, FavoniusWarbow]

artifactSets = [[artifacts.TF(2), artifacts.Glad(2)],
                    [artifacts.Shime(2), artifacts.Glad(2)],
                    [artifacts.TF(2)],
                    [artifacts.Glad(2)],
                    [],
                    [artifacts.TS(4)],
                    [artifacts.TOM(4)]]



def calc_weapon(rotation, weapon, artifact_sets: list, character_creators: list):
    bad = weapon()
    personal = [f"{bad.name}"]
    team = [f"{bad.name}"]
    for s in artifact_sets:
        for r in range(1, 6):
            w = weapon(refinement=r)
            fish = character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=s)
            length = rotation["length"]
            rot = Rotation(rotation["list"],
                           characters=[character_creators[0](),
                                       character_creators[0](),
                                       character.Kazuha(),
                                       fish],
                           length=length)
            rot.do_rotation()
            personal.append(rot.damageDict[fish] / length)
            team.append(rot.damage / length)
    return personal, team


def execute_rotation(weapons: list, artifact_sets: list):
    with Pool() as pool:
        for i in pool.map(calc_weapon, artifact_sets):
            pass


if __name__ == '__main__':
    #taser(artifactSets, weapons)
    test()
    #aggravate("aggravateEMEM")
    #bad2("sukokomon")
    #bad("raifish")
    #test()
