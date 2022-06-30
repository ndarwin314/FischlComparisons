
"""weapons = (PolarStar, Water, SkywardHarp, ThunderingPulse, AmosBow, ElegyForTheEnd,
               PrototypeCrescent, TheStringless, MouunsMoon,
               WindblumeOde, AlleyHunter, TheViridescentHunt, FavoniusWarbow,
               SacrificialBow, MitternachtsWaltz, Hamayumi, Rust, Twilight)"""

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