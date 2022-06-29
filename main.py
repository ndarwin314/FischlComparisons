# import fischl
# from fischl import Set
import csv
import time
from rotation import *
import character
from actions import Skill, Charged, Normal, Burst, Swap, Reaction
from weapons import *

"""weapons = (PolarStar, Water, SkywardHarp, ThunderingPulse, AmosBow, ElegyForTheEnd,
               PrototypeCrescent, TheStringless, MouunsMoon,
               WindblumeOde, AlleyHunter, TheViridescentHunt, FavoniusWarbow,
               SacrificialBow, MitternachtsWaltz, Hamayumi, Rust, Twilight)"""


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
                    row.append(str(test.kqm_optimize(test.rotation_raifish, sweaty=True)))
            CSV.append(row)
    print(time.time() - start)
    with open('results/raifish.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV:
            writer.writerow(line)


def yelan_moment():
    start = time.time()
    artifactSets = [[Set.G, Set.ATK], [Set.G, Set.TF], [Set.G]]
    # this is bad code but it runs once so idc
    slots = []
    for i in range(5):
        for j in range(i + 1, 5):
            slots.append([ArtifactSlots(i), ArtifactSlots(j)])
    CSV = [["weapon"] + 7 * ["r1", "r2", "r3", "r4", "r5"]]
    for artifact in artifactSets:
        for slot in slots:
            CSV.append([f"{artifact_set_name(artifact)}, {slot[0].name}, {slot[1].name}"])
            for weapon in weapons:
                bad = weapon()
                row = [f"{bad.name}"]
                for constellation in range(7):
                    for r in range(1, 6):
                        w = weapon(refinement=r)
                        test = fischl.Fischl(9, 9, 9, constellation=constellation,
                                             weapon=w, artifact_set=artifact, gambler_slots=slot)
                        row.append(str(test.kqm_optimize(test.rotation_raifish, sweaty=True)))
                CSV.append(row)
    print(time.time() - start)
    with open('results/gamblerRaifish.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV:
            writer.writerow(line)


def test():
    f = fischl.Fischl(9, 9, 9, constellation=6, weapon=PrototypeCrescent(), artifact_set=[Set.ATK, Set.TF])
    f.kqm_optimize(f.rotation_raifishSuc, sweaty=True)
    print(f.artifactStats)
    print(f.get_stats())
    print(f.rotation_raifishSuc())
    g = fischl.Fischl(9, 9, 9, constellation=6, weapon=PrototypeCrescent(), artifact_set=[Set.ATK, Set.TF])
    g.kqm_optimize(g.rotation_raifish, sweaty=True)
    print(g.artifactStats)
    print(g.get_stats())
    print(g.rotation_raifish())


rot = [Skill(0, 0),
       Swap(2, 0.62),
       Skill(2, 0.85, infusion=Element.ELECTRO),
       Reaction(2, 1.1, Reactions.ELECTROSWIRL),
       Reaction(2, 1.9, Reactions.ELECTROSWIRL),
       Swap(1, 1.9),
       Skill(1, 2.13),
       Reaction(1, 2.42, Reactions.OVERLOAD),
       Burst(1, 2.85),
       Swap(3, 3.72),
       Normal(3, 4.37, 1),
       Charged(3, 4.5),
       Reaction(0, 4.47, Reactions.OVERLOAD),
       Burst(3, 4.58),
       Reaction(3, 4.73, Reactions.OVERLOAD),
       Swap(2, 5),
       Burst(2, 5.23, infusion=Element.PYRO),
       Reaction(2, 6.62, Reactions.ELECTROSWIRL),
       Swap(0, 6.83),
       Burst(0, 7.07),
       Reaction(2, 7.7, Reactions.ELECTROSWIRL),
       Reaction(2, 7.7, Reactions.OVERLOAD),
       Normal(0, 9.13, 1),
       Normal(0, 9.48, 2),
       Normal(0, 9.73, 3),
       Charged(0, 10.53),
       Reaction(2, 9.65, Reactions.ELECTROSWIRL),
       Reaction(2, 9.65, Reactions.OVERLOAD),
       Normal(0, 11.28, 1),
       Normal(0, 11.63, 2),
       Normal(0, 11.88, 3),
       Charged(0, 12.68),
       Reaction(2, 11.6, Reactions.ELECTROSWIRL),
       Reaction(2, 11.6, Reactions.OVERLOAD),
       Normal(0, 13.43, 1),
       Normal(0, 13.78, 2),
       Normal(0, 14.03, 3),
       Charged(0, 14.83),
       Reaction(2, 13.55, Reactions.ELECTROSWIRL),
       Reaction(2, 13.55, Reactions.OVERLOAD),
       Swap(3, 15.37),
       Reaction(2, 15.5, Reactions.ELECTROSWIRL),
       Reaction(2, 15.5, Reactions.OVERLOAD),
       Charged(3, 15.55),
       Normal(3, 15.55, 1),
       Skill(3, 15.6),
       Swap(2, 16.6),
       Skill(2, 16.83, infusion=Element.PYRO),
       Reaction(2, 17.08, Reactions.ELECTROSWIRL),
       Reaction(2, 17.87, Reactions.ELECTROSWIRL),
       Reaction(2, 17.87, Reactions.OVERLOAD),
       Normal(3, 18, 1),  # fuck
       Normal(3, 18.5, 1),
       ]
if __name__ == '__main__':
    w = WindblumeOde()
    test = Rotation(rot, [character.Raiden(), character.Bennett(), character.Kazuha(), character.Fischl(weapon=w)],
                    enemy_count=1)
    test.do_rotation()
    print(test.damage / 19, w)
    print({char: d / 19 for char, d in test.damageDict.items()})
    """we = [AlleyHunter(refinement=1), AlleyHunter(refinement=5), ThunderingPulse(refinement=1), PolarStar(refinement=1),
          Water(refinement=1), ElegyForTheEnd(refinement=1), SkywardHarp(refinement=1), PrototypeCrescent(refinement=1),
          PrototypeCrescent(refinement=5), TheStringless(refinement=1), TheStringless(refinement=5),
          MouunsMoon(refinement=5), WindblumeOde()]
    for w in we:
        test = Rotation(rot, [character.Raiden(), character.Bennett(), character.Kazuha(), character.Fischl(weapon=w)],
                        enemy_count=1)
        test.do_rotation()
        print(test.damage / 19, w)
        print({char: d / 19 for char, d in test.damageDict.items()})"""
    """test = Rotation(rot,
                    [character.Raiden(), character.Bennett(), character.Kazuha(),
                     character.Fischl(artifact_set=(art.SetCount(art.Set.TOM, 4),))])
    test.do_rotation()
    print(test.damage / 19)
    print({char: d / 19 for char, d in test.damageDict.items()})
    test = Rotation(rot,
                    [character.Raiden(), character.Bennett(), character.Kazuha(),
                     character.Fischl(artifact_set=(art.SetCount(art.Set.TS, 4),))])
    test.do_rotation()
    print(test.damage / 19)
    print({char: d / 19 for char, d in test.damageDict.items()})"""
