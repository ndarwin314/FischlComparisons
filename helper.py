import csv
import time
from multiprocessing import Pool

import numpy as np

import artifacts
from artifacts import Set, SetCount
from rotation import *
import character
from weapons import *
from action_lists import RaiFish, Sukokomon, aggravateFish, Test, Taser, raidenTest

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

def give_up(rot_name, artifact_sets, weapon_list, length, rot_creator, fischl_creator, auto):
    personalCSV, teamCSV, temp = create_csvs(artifact_sets, weapon_list, length, rot_creator, fischl_creator, auto)
    write(rot_name, personalCSV, teamCSV)

def create_csvs(artifact_sets, weapon_list, length, rot_creator, fischl_creator, auto):
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
                fish = fischl_creator(w, artifact)
                rot = rot_creator(fish)
                if not auto:
                    fish.greedy_optim(output=(r==1) and (artifact==[artifacts.TF(2), artifacts.Glad(2)]))
                rot.do_rotation()
                personal.append(rot.damageDict[fish] / length)
                damage += rot.damageDict[fish] / length
                team.append(rot.damage / length)
                # print(rot.damageDict)
                del rot
                del fish
                del w
            personal.append(" ")
            team.append(" ")
        print(weapon)
        personalCSV.append(personal)
        teamCSV.append(team)
    return personalCSV, teamCSV, damage/(len(weapon_list)*len(artifact_sets))


@timer
def aggravate(artifact_sets, weapon_list, auto=False):
    rot_creator = lambda fish:  Rotation(aggravateFish["list"],
                               characters=[character.Raiden(),
                                           character.Collei(artifact_set=[artifacts.Instructor(4)]),
                                           character.Kazuha(),
                                           fish],
                               length=36)
    fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact,
                                                          aggravate=1, auto_artis=auto)
    give_up("aggravateFish2", artifact_sets, weapon_list, 36, rot_creator, fischl_creator, auto)



@timer
def taser(artifact_sets, weapon_list, auto=False):
    length = Taser["length"]
    fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact,
                                                          er_requirement=1.3, auto_artis=auto)
    rot_creator = lambda fish: Rotation(Taser["list"],
                               characters=[character.Beidou(weapon=Akuoumaru()), fish, character.Xingqiu(), character.Sucrose(weapon=SacFrags())],
                               length=length,
                               enemy_count=2)
    give_up("taser", artifact_sets, weapon_list, length, rot_creator, fischl_creator, auto)

timer
def raifish(artifact_set, weapon_list, auto):
    length = Test["length"]
    rotation_creator = lambda fish: Rotation(Test["list"],
                                   characters=[character.Raiden(), character.Bennett(), character.Kazuha(), fish],
                                   length=length)
    fish_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact,
                                                         auto_artis=auto)
    give_up("raifish", artifact_set, weapon_list, length, rotation_creator, fish_creator, auto)


@timer
def funny_soup_team(artifact_set, weapon_list, auto):
    length = Sukokomon["length"]
    fish_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=6, weapon=w, artifact_set=artifact,
                                                        er_requirement=1.5, auto_artis=auto)
    rotation_creator = lambda fish: Rotation(Sukokomon["list"],
                                             characters=[character.Sucrose(weapon=SacFrags()),
                                                         character.Kokomi(weapon=TTDS()),
                                                         fish,
                                                         character.Xiangling(weapon=Kitain())],
                                             length=25.5)
    give_up("sukokomon", artifact_set, weapon_list, length, rotation_creator, fish_creator, auto)

@timer
def test(con=6):
    w = PrototypeCrescent(refinement=5)
    length = 21.3
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[artifacts.TF(2), artifacts.Glad(2)], constellation=con)
    rot = Rotation(Taser["list"],
                   characters=[character.Beidou(weapon=Akuoumaru()), fish, character.Xingqiu(),
                               character.Sucrose(weapon=SacFrags())],
                   length=length,
                   enemy_count=2, logging="logTaser.csv")
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})
    return rot.damageDict[fish]

@timer
def test2():
    rot = Rotation(Sukokomon["list"],
                   characters=[character.Sucrose(weapon=SacFrags()),
                               character.Kokomi(weapon=TTDS()),
                               fish:=character.Fischl(er_requirement=1.4, weapon=Magic(refinement=1)),
                               character.Xiangling(weapon=Kitain())],
                   length=25.5, logging="logSuko.csv")
    rot.do_rotation()
    print(rot.damage / 25)
    print({k: round(v / 25, 2) for k,v in rot.damageDict.items()})
    return rot.damageDict[fish]

@timer
def test3():
    w = AlleyHunter(refinement=1)
    length = Test["length"]
    fish = character.Fischl(9, 9, 9, weapon=w)
    rot = Rotation(Test["list"], characters=[
        character.Raiden(artifact_set=[artifacts.Emblem(4)]),
        character.Bennett(),
        character.Kazuha(),
        fish],
                   length=length, logging="logRaifish.csv")
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})
    return rot.damageDict[fish]

@timer
def gt_test():
    w = AlleyHunter(refinement=1)
    length = Test["length"]
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[artifacts.GT(4)])
    rot = Rotation(Test["list"], characters=[
        character.Raiden(artifact_set=[artifacts.Emblem(4)]),
        character.Bennett(),
        character.Kazuha(),
        fish],
                   length=length, logging="gt.csv")
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})
    return rot.damageDict[fish]


@timer
def test4():

    w = TheStringless(refinement=3)
    length = aggravateFish["length"]
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[artifacts.TF(2), artifacts.Glad(2)])
    rot = Rotation(aggravateFish["list"], characters=[
        character.Raiden(),
        character.Collei(artifact_set=[artifacts.Instructor(4)]),
        character.Kazuha(),
        fish],
        length=length, logging="logAggravate.csv")
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})
    return rot.damageDict[fish]

@timer
def test4():
    w = TheStringless(refinement=3)
    length = aggravateFish["length"]
    fish = character.Fischl(9, 9, 9, weapon=w, artifact_set=[artifacts.TF(2), artifacts.Glad(2)])
    rot = Rotation(aggravateFish["list"], characters=[
        character.Raiden(),
        character.Collei(artifact_set=[artifacts.Instructor(4)]),
        character.Kazuha(),
        fish],
        length=length, logging="logAggravate.csv")
    fish.greedy_optim()
    rot.do_rotation()
    print(rot.damage / length)
    print({k: round(v/length,2) for k,v in rot.damageDict.items()})
    return rot.damageDict[fish]


@timer
def con_comparison(artifact_sets, weapon_list):
    bad_array = np.zeros((7, 4))
    percent_array = np.zeros((7, 4))
    average_array = np.ones(7)
    percent_array[0] = 1
    csv_array = [[] for _ in range(4)]
    for i in range(7):
        bad = []
        length = Taser["length"]
        fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=i, weapon=w, artifact_set=artifact,
                                                          er_requirement=1.3)
        rot_creator = lambda fish: Rotation(Taser["list"],
                                            characters=[character.Beidou(weapon=Akuoumaru()), fish, character.Xingqiu(),
                                                        character.Sucrose(weapon=SacFrags())],
                                            length=length,
                                            enemy_count=1)
        a, b, current = create_csvs(artifact_sets, weapon_list, length, rot_creator, fischl_creator)
        csv_array[0] += a
        bad.append(current)
        length = Test["length"]
        rot_creator = lambda fish: Rotation(Test["list"],
                                                 characters=[character.Raiden(), character.Bennett(),
                                                             character.Kazuha(), fish],
                                                 length=length)
        fish_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=i, weapon=w,
                                                               artifact_set=artifact)
        a, b, current = create_csvs(artifact_sets, weapon_list, length, rot_creator, fish_creator)
        csv_array[1] += a
        bad.append(current)
        rot_creator = lambda fish: Rotation(aggravateFish["list"],
                                            characters=[character.Raiden(),
                                                        character.Collei(artifact_set=[artifacts.Instructor(4)]),
                                                        character.Kazuha(),
                                                        fish],
                                            length=36)
        fischl_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=i, weapon=w, artifact_set=artifact,
                                                              aggravate=1)
        a, b, current = create_csvs(artifact_sets, weapon_list, length, rot_creator, fischl_creator)
        csv_array[2] += a
        bad.append(current)
        fish_creator = lambda w, artifact: character.Fischl(9, 9, 9, constellation=i, weapon=w, artifact_set=artifact,
                                                           er_requirement=1.5)
        rot_creator = lambda fish: Rotation(Sukokomon["list"],
                                                 characters=[character.Sucrose(weapon=SacFrags()),
                                                             character.Kokomi(weapon=TTDS()),
                                                             fish,
                                                             character.Xiangling(weapon=Kitain())],
                                                 length=25.5)
        a, b, current = create_csvs(artifact_sets, weapon_list, length, rot_creator, fish_creator)
        csv_array[3] += a
        bad.append(current)
        bad_array[i] = bad
        if i == 0:
            print(f"increase over previous {i}: 1")
            print(f"increase over c0 {i}: 1")
        else:
            percent_array[i] = bad_array[i] / bad_array[i-1]
            average_array[i] = np.mean(percent_array[i])
            print(f"increase over previous {i}: {average_array[i]}")
            print(f"increase over c0 {i}: {np.prod(average_array)}")
    print(np.prod(average_array))
    with open('results2/constellation.csv', 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for i in range(len(csv_array[0])):
            writer.writerow(sum([csv_array[j][i] for j in range(4)], start=[]))


