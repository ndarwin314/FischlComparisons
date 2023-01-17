import csv
import time
from multiprocessing import Pool

import artifacts
from artifacts import Set, SetCount
from rotation import *
import character
from weapons import *
from action_lists import RaiFish, Sukokomon, aggravateFish, Test, Taser

default_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact)

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
    return "".join(name)[:-2]

def write(name, CSV, CSV2):
    with open('results2/' + name + '.csv', 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV:
            writer.writerow(line)
    with open('results2/' + name + 'TeamDPS.csv', 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in CSV2:
            writer.writerow(line)

@timer
def raifish(artifact_set, weapon_list):
    length = Test["length"]
    rotation_creator = lambda fish: Rotation(Test["list"],
                                   characters=[character.Raiden(), character.Bennett(), character.Kazuha(), fish],
                                   length=length)
    give_up("raifish", artifact_set, weapon_list, length, rotation_creator, default_creator)


@timer
def funny_soup_team(artifact_set, weapon_list):
    length = Sukokomon["length"]
    fish_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact, er_requirement=1.5)
    rotation_creator = lambda fish: Rotation(Sukokomon["list"],
                                             characters=[character.Sucrose(weapon=SacFrags()),
                                                         character.Kokomi(weapon=TTDS()),
                                                         fish,
                                                         character.Xiangling(weapon=Kitain())],
                                             length=25.5)
    give_up("sukokomon", artifact_set, weapon_list, length, rotation_creator, fish_creator)

def give_up(rot_name, artifact_sets, weapon_list, length, rot_creator, fishl_creator):
    personalCSV, teamCSV, temp = create_csvs(artifact_sets, weapon_list, length, rot_creator, fishl_creator)
    write(rot_name, personalCSV, teamCSV)

def create_csvs(artifact_sets, weapon_list, length, rot_creator, fishl_creator):
    refinementList = ["r1", "r2", "r3", "r4", "r5"]
    personalCSV = [["weapon"]]
    teamCSV = [["weapon"]]
    damage = 0
    for s in artifact_sets:
        name = artifact_set_name(s)
        personalCSV[0].append(name)
        personalCSV[0] += refinementList
        teamCSV[0].append(name)
        teamCSV[0] += refinementList
    for weapon in weapon_list:
        bad = weapon()
        personal = [f"{bad.name}", ""]
        team = [f"{bad.name}", ""]
        for artifact in artifact_sets:
            for r in range(1, 6):
                w = weapon(refinement=r)
                fish = fishl_creator(w, artifact)
                rot = rot_creator(fish)
                rot.do_rotation()
                personal.append(rot.damageDict[fish] / length)
                damage += rot.damageDict[fish] / length
                team.append(rot.damage / length)
                # print(rot.damageDict)
            personal.append(" ")
            team.append(" ")
        personalCSV.append(personal)
        teamCSV.append(team)
    return personalCSV, teamCSV, damage/(len(weapon_list)*len(artifact_sets))


@timer
def aggravate(artifact_sets, weapon_list):
    rot_creator = lambda fish:  Rotation(aggravateFish["list"],
                               characters=[character.Raiden(),
                                           character.Collei(artifact_set=[artifacts.Instructor(4)]),
                                           character.Kazuha(),
                                           fish],
                               length=36)
    fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact, aggravate=1)
    give_up("aggravateFish", artifact_sets, weapon_list, 36, rot_creator, fischl_creator)



@timer
def taser(artifact_sets, weapon_list):
    length = Taser["length"]
    fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact, er_requirement=1.3)
    rot_creator = lambda fish: Rotation(Taser["list"],
                               characters=[character.Beidou(weapon=Akuoumaru()), fish, character.Xingqiu(), character.Sucrose(weapon=SacFrags())],
                               length=length,
                               enemy_count=2)
    give_up("taser", artifact_sets, weapon_list, length, rot_creator, fischl_creator)

@timer
def test():
    w = PrototypeCrescent(refinement=5)
    # [SetCount(Set.TF, 2), SetCount(Set.ATK, 2)]
    length = 21.3
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[artifacts.TF(2), artifacts.Glad(2)])
    rot = Rotation(Taser["list"],
                   characters=[character.Beidou(weapon=Akuoumaru()), fish, character.Xingqiu(weapon=FavoniusWarbow()),
                               character.Sucrose(weapon=SacFrags())],
                   length=length,
                   enemy_count=2)
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})

@timer
def test2():
    rot = Rotation(Sukokomon["list"],
                   characters=[character.Sucrose(weapon=SacFrags()),
                               character.Kokomi(weapon=TTDS()),
                               character.Fischl(er_requirement=1.4, weapon=ElegyForTheEnd(refinement=1)),
                               character.Xiangling(weapon=Kitain())],
                   length=25.5)
    rot.do_rotation()
    print(rot.damage / 25)
    print({k: round(v / 25, 2) for k,v in rot.damageDict.items()})

@timer
def test3():
    w = AlleyHunter(refinement=1)
    length = Test["length"]
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[SetCount(Set.TF, 2), SetCount(Set.ATK, 2)])
    rot = Rotation(Test["list"], characters=[
        character.Raiden(artifact_set=[SetCount(Set.EMBLEM, 4)]),
        character.Bennett(),
        character.Kazuha(),
        fish],
                   length=length)
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})

@timer
def test4():
    w = TheStringless(refinement=3)
    length = aggravateFish["length"]
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[artifacts.TS(4)])
    rot = Rotation(aggravateFish["list"], characters=[
        character.Raiden(),
        character.Collei(artifact_set=[artifacts.NO(4)]),
        character.Kazuha(),
        fish],
        length=length)
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})

@timer
def con_comparison(artifact_sets, weapon_list):
    for i in range(7):
        length = Taser["length"]
        fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=i, weapon=w, artifact_set=artifact,
                                                          er_requirement=1.3)
        rot_creator = lambda fish: Rotation(Taser["list"],
                                            characters=[character.Beidou(weapon=Akuoumaru()), fish, character.Xingqiu(),
                                                        character.Sucrose(weapon=SacFrags())],
                                            length=length,
                                            enemy_count=2)
        a, b, c = create_csvs(artifact_sets, weapon_list, length, rot_creator, fischl_creator)
        print(c)
