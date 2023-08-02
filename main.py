from helper import *

weapons = [PolarStar, Water, Hunter, SkywardHarp, ThunderingPulse, TheViridescentHunt, AmosBow, AlleyHunter,
           PrototypeCrescent,Twilight, MouunsMoon, ElegyForTheEnd, Rust, TheStringless, Hamayumi, WindblumeOde,
           SacrificialBow, FavoniusWarbow, Ibis, Magic]

artifactSets = [
    [artifacts.TF(2), artifacts.Glad(2)],
    [artifacts.TF(2), artifacts.Gilded(2)],
    [artifacts.TF(2)],
    [artifacts.TF(4)],
    [artifacts.Shime(2), artifacts.Glad(2)],
    [artifacts.Shime(2), artifacts.Gilded(2)],
    [artifacts.Shime(2)],
    [artifacts.Gilded(2), artifacts.Gilded(2)],
    [artifacts.Gilded(2)],
    [],
    [artifacts.TS(4)],
    [artifacts.TOM(4)],
    [artifacts.Gilded(4)],
    [artifacts.GT(2)],
    [artifacts.GT(2), artifacts.TF(2)],
    [artifacts.GT(2), artifacts.Glad(2)],
    [artifacts.GT(2), artifacts.Gilded(2)],
    [artifacts.GT(4)]]

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
    #test_greedy()
    t = True
    if t:
        test()
        test2()
        test3()
        test4()
    else:
        aggravate(artifactSets, weapons)
        taser(artifactSets, weapons)
        raifish(artifactSets, weapons)
        funny_soup_team(artifactSets, weapons)
    #con_comparison(artifactSets, weapons)
