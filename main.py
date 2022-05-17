import fischl
from fischl import Set
from bows import *
import csv
import time
from attributes import*
from random import random as r

def artifact_set_name(array):
    if not array:
        return "Rainbow"
    name = []
    for s in array:
        if s == Set.TF or s == Set.ATK:
            name.append(f"2 {s.name} ")
        elif s == Set.TS:
            name.append("4 TS ")
    return "".join(name)

def main():
    start = time.time()
    weapons = (PolarStar, Water, SkywardHarp, ThunderingPulse, AmosBow, ElegyForTheEnd,
               PrototypeCrescent, TheStringless, MouunsMoon,
               WindblumeOde, AlleyHunter, TheViridescentHunt, FavoniusWarbow,
               SacrificialBow, MitternachtsWaltz, Hamayumi, Rust)
    # weapons = (PolarStar(), ThunderingPulse(), SkywardHarp(), Water())
    artifactSets = [[Set.TF, Set.ATK], [Set.ATK, Set.ATK], [Set.TF], [Set.ATK], [], [Set.TS]]
    CSV = [["weapon"] + 7 * ["r1", "r2", "r3", "r4", "r5"]]
    for artifact in artifactSets:
        CSV.append([f"{artifact_set_name(artifact)}"])
        for weapon in weapons:
            bad = weapon()
            row = [f"{bad.name}"]
            for constellation in range(7):
                for r in range(1, 6):
                    w = weapon(refinement=r)
                    test = fischl.Fischl(9, 9, 9, constellation=constellation, weapon=w, artifact_set=artifact)
                    row.append(str(test.kqm_optimize(test.rotation_sukokomon, sweaty=True)))
            CSV.append(row)
    print(time.time() - start)
    with open('sukokomon.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV:
            writer.writerow(line)


if __name__ == '__main__':
    main()

