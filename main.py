import csv
import time
from artifacts import Set, SetCount
from rotation import *
import character
from weapons import *
from action_lists import RaiFish
import actions

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        print(time.time()-start)
    return wrapper


def artifact_set_name(array):
    if not array:
        return "Rainbow"
    name = []
    for s in array:
        name.append(f"{str(s)}, ")
    return "".join(name)



@timer
def bad(name):
    weapons = [PolarStar, Water, SkywardHarp, ThunderingPulse, TheViridescentHunt, AmosBow, AlleyHunter, PrototypeCrescent,
               Twilight, MouunsMoon, ElegyForTheEnd, Rust, TheStringless, Hamayumi, WindblumeOde, SacrificialBow, FavoniusWarbow]
    artifactSets = [[SetCount(Set.TF, 2), SetCount(Set.ATK, 2)],
                    [SetCount(Set.ATK, 2), SetCount(Set.ATK, 2)],
                    [SetCount(Set.TF, 2)],
                    [SetCount(Set.ATK, 2)],
                    [],
                    [SetCount(Set.TS, 4)],
                    [SetCount(Set.TOM, 4)]]
    length = 36
    CSV = [["weapon"] + 7 * ["r1", "r2", "r3", "r4", "r5"]]
    CSV2 = [["weapon"] + 7 * ["r1", "r2", "r3", "r4", "r5"]]
    for artifact in artifactSets:
        CSV.append([f"{artifact_set_name(artifact)}"])
        CSV2.append([f"{artifact_set_name(artifact)}"])
        for weapon in weapons:
            bad = weapon()
            row = [f"{bad.name}"]
            row2 = [f"{bad.name}"]
            for constellation in range(7):
                for r in range(1, 6):
                    w = weapon(refinement=r)
                    fish = character.Fischl(9, 9, 9, constellation=constellation, weapon=w, artifact_set=artifact)
                    rot = Rotation(RaiFish["list"],
                                   characters=[character.Raiden(), character.Bennett(), character.Kazuha(), fish],
                                   length=length)
                    rot.do_rotation()
                    row.append(rot.damageDict[fish] / length)
                    row2.append(rot.damage / length)
            CSV.append(row)
            CSV2.append(row2)
    with open('results2/' + name + '.csv', 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV:
            writer.writerow(line)
    with open('results2/' + name + 'TeamDPS.csv', 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV2:
            writer.writerow(line)

@timer
def test():
    w = AlleyHunter()
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[SetCount(Set.TF, 2), SetCount(Set.ATK, 2)])
    rot = Rotation(RaiFish["list"], characters=[character.Raiden(), character.Bennett(), character.Kazuha(), fish],
                   length=36)
    rot.do_rotation()
    print({k: round(v/36,2) for k,v in rot.damageDict.items()})

@timer
def test2():
    w = AlleyHunter()
    rot = Rotation([actions.Burst(0,0), actions.Skill(0,1), actions.Swap(2, 1.5), actions.Burst(2, 2), actions.Swap(1, 2.5), actions.Burst(1, 3), actions.Skill(1, 3.5), actions.Swap(0, 4)],
                   characters=[character.Kokomi(), character.Xiangling(), character.Bennett()],
                   length=36)
    rot.do_rotation()
    print({k: round(v,2) for k,v in rot.damageDict.items()})

if __name__ == '__main__':
    #bad("raifish")
    test()
