import fischl
from fischl import Set
from bows import *
from attributes import*


if __name__ == '__main__':  
    weapons = (PolarStar, Water, SkywardHarp, ThunderingPulse, AmosBow, ElegyForTheEnd,
               PrototypeCrescent, TheStringless, MouunsMoon,
               WindblumeOde, AlleyHunter, TheViridescentHunt, FavoniusWarbow,
               SacrificialBow, MitternachtsWaltz, Hamayumi, Rust)
    #weapons = (PolarStar(), ThunderingPulse(), SkywardHarp(), Water())
    csv = [["weapon", "r1", "r2", "r3", "r4", "r5"]]
    for weapon in weapons:
        bad = weapon()
        row = [f"{bad.name}"]
        for i in range(1, 6):
            w = weapon(refinement=i)
            test = fischl.Fischl(9, 9, 6, w, [Set.TS])
            row.append(str(test.kqm_optimize(test.rotation_sukokomon, sweaty=True)))
        csv.append(row)
    np.savetxt("sukokomon4TS.csv", csv, delimiter=",", fmt='%s')


