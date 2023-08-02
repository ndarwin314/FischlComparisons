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

if __name__ == '__main__':
    #test_greedy()
    #aggravate(artifactSets, weapons, False)
    raifish(artifactSets, weapons, False)
    """t = True
    if t:
        test()
        test2()
        test3()
        test4()
    else:
        aggravate(artifactSets, weapons)
        taser(artifactSets, weapons)
        raifish(artifactSets, weapons)
        funny_soup_team(artifactSets, weapons)"""
    #con_comparison(artifactSets, weapons)
