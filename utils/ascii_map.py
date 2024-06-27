# given a game set up (e.g., layer01), display ascii map with veggie locations

import numpy as np
import csv
from datetime import datetime
import os

def get_target_loc(target, legal_moves):
    moves = []
    #twelve possible layers, "Items00" thru "Items11"
    moves = legal_moves.split(' ')
    if target=="timeout" or "Pillow" in target:
        target='none'
    move = next(m for m in moves if target in m)
    x,y = move.split('(')[-1].split('(')[-1].strip(")").split(',')
    return int(x), int(y)

def get_items_from_layer(layer, coloronly = False): #twelve possible layers, "Items00" thru "Items11"
    # configure how to get list of veggies from a given starting setup (one of the twelve object layers)
    # print(os.getcwd())
    fname = os.getcwd() + "/utils/game_configs.csv"
    objectlayers = {}

    with open(fname, 'r') as data:
        for line in csv.DictReader(data):
            layername = line["objectLayer"]
            farmitems = line["farmItems"].strip("']['").split(' ')
            # print(layername)
            objectlayers[layername]=farmitems

    # CODE for veggies:
        # o = tomato
        # s = strawberry
        # e = eggplant
        # t = turnip
    vegcode = {'tomato':'o', 'strawberry':'s', 'eggplant':'e', 'turnip':'t'}

    veggies = []
    #twelve possible layers, "Items00" thru "Items11"
    for vegstr in objectlayers[layer]:
        # veggie str looks something like: 'Tomato00(8,7)' or 'Strawberry00(7,7)'
        name = vegstr.split('0')[0].lower()
        x,y = vegstr.split('(')[-1].split('(')[-1].strip(")").split(',')
        if coloronly:
            id = 'r' if name=="tomato" or name=="strawberry" else 'p'
        else: 
            id = vegcode[name]

        veggies.append((int(x),int(y),id))
    return veggies

def get_items_from_string(farmItemsStr, farmonly = True, coloronly = False):

    farmitems = farmItemsStr.split(' ')

    # CODE for veggies:
        # o = tomato
        # s = strawberry
        # e = eggplant
        # t = turnip
    vegcode = {'tomato':'o', 'strawberry':'s', 'eggplant':'e', 'turnip':'t'}

    veggies = []
    #twelve possible layers, "Items00" thru "Items11"
    for vegstr in farmitems:
        # veggie str looks something like: 'Tomato00(8,7)' or 'Strawberry00(7,7)'
        name = vegstr.split('0')[0].lower()
        x,y = vegstr.split('(')[-1].split('(')[-1].strip(")").split(',')
        if (farmonly and (int(x) < 20)) or (not farmonly): # we only want items in the bounds of the map (not backpack)
            if coloronly:
                id = 'r' if name=="tomato" or name=="strawberry" else 'p'
            else: 
                id = vegcode[name]
            veggies.append((int(x),int(y),id))

    return veggies

# veglist is either acquired from get_items_list(layer) or the string list saved in farmitems
# chars = [(x,y,'R'),(x,y,'P')]
def print_mapstr(veglist, chars):
    rows = 20
    cols = 20
    content = [["."]*cols for _ in range(rows)]

    #       0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19
    map = [[1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], # 0
        [1., 1., 0., 0., 0., 0., 1., 1., 1., 1., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 1
        [1., 0., 0., 0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 2
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 3
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 4
        [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 0., 1., 1., 1.], # 5
        [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 6
        [1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 7
        [1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 8
        [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 9
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 10
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 11
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1.], # 12
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1.], # 13
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1.], # 14
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1.], # 15
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1.], # 16
        [1., 1., 0., 0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1.], # 17
        [1., 1., 1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1.], # 18
        [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]] # 19


    # boundaries is a list of (x,y) tuples where value of map is 1
    boundaries = list(zip(*np.where(np.array(map) == 1)))
    for (x,y) in boundaries: content[x][y] = 'x'

    # NOTE: for veggies and chars, their x y terms are swappy
    # now add the veggies
    for (x,y,s) in veglist: content[y][x] = s

    # add the chars
    for (x,y,s) in chars: content[y][x] = s

    # build frame
    width       = len(str(max(rows,cols)-1))
    contentLine = "# | values |"

    dashes      = "-".join("-"*width for _ in range(cols))
    frameLine   = contentLine.replace("values",dashes)
    frameLine   = frameLine.replace("#"," "*width)
    frameLine   = frameLine.replace("| ","+-").replace(" |","-+")

    # print grid
    print(frameLine)
    for i,row in enumerate(content,1):
        values = " ".join(f"{v:{width}s}" for v in row)
        line   = contentLine.replace("values",values)
        line   = line.replace("#",f"{rows-i:{width}d}")
        print(line)
    print(frameLine)

    # x-axis numbers
    numLine = contentLine.replace("|"," ")
    numLine = numLine.replace("#"," "*width)
    colNums = " ".join(f"{i:<{width}d}" for i in range(cols))
    numLine = numLine.replace("values",colNums)
    print(numLine)


def print_transcript(df, sesh, game):
    thisgame = df[(df["session"]==sesh) & (df["gameNum"]==game)]

    print("Showing game " + str(game) + " from session " + sesh)
    print("Condition: " + thisgame["resourceCond"].iloc[0] + " " + thisgame["visibilityCond"].iloc[0] + " " + thisgame["costCond"].iloc[0])
    print("Red BP capacity: " + str(thisgame["redBackpackSize"].iloc[0]) + ", Purple BP capacity: " + str(thisgame["purpleBackpackSize"].iloc[0]))
    print("start time: " + str(datetime.fromtimestamp(thisgame["turnStartTimestamp"].iloc[0]/1000)))

    # red starts at 'x':2, 'y':15
    # purple starts at 'x':3, 'y':16
    # chars = [(2,15,'R'),(3,16,'P')]
    # chars = [(thisgame["redXloc"].iloc[0],thisgame["redYloc"].iloc[0],'R'),(thisgame["purpleXloc"].iloc[0],thisgame["purpleYloc"].iloc[0],'P')]

    # veglist = get_items_from_layer(thisgame["objectLayer"].unique()[0])
    # print_mapstr(veglist, chars)

    for i in sorted(thisgame['trialNum'].unique()):
        trial = thisgame[thisgame['trialNum']==i].iloc[0] # one row of the dataframe
        # print(trial['gameover'])

        # print map current status
        chars = [(trial["redXloc"],trial["redYloc"],'R'),(trial["purpleXloc"],trial["purpleYloc"],'P')]
        veglist = get_items_from_string(trial["farmItems"])
        print_mapstr(veglist, chars)

        if trial['gameover']:
            # end of game
            print("END OF GAME!")
            print("Red energy="+str(trial['redEnergy'])+", score=" + str(trial['redScore']) + ": BONUS="+str(trial['redPoints']))
            print("Purple energy="+str(trial['purpleEnergy'])+", score=" + str(trial['purpleScore']) + ": BONUS="+str(trial['purplePoints']))
        else: 
            # print char backpacks and farm box contents
            print("\n*** turn " + str(trial['turnCount'])+ ": " + trial['agent'] + "'s turn! ***")

            # print("Timestamp: " + str(datetime.fromtimestamp(trial["decisionMadeTimestamp"]/1000)))
            print("red backpack: " + str(trial["redBackpack"]))
            print("purple backpack: " + str(trial["purpleBackpack"]))
            print("harvest box: " + str(trial["farmBox"]))
            # print(chars)
                        
            # print current scores
            print("Red energy="+str(trial['redEnergy'])+", score=" + str(trial['redScore']))
            print("Purple energy="+str(trial['purpleEnergy'])+", score=" + str(trial['purpleScore']))

            # print player choice
            print(trial['agent'].capitalize() + " player picks " + trial['target'] + ". Response time: " + str(int(trial['responseTime'])) + "ms.")

        # chars = [(trial["redXloc"],trial["redYloc"],'R'),(trial["purpleXloc"],trial["purpleYloc"],'P')]
        # # print map current status
        # veglist = get_items_from_string(trial["farmItems"])
        # print_mapstr(veglist, chars)
        # # try:
        #     chars = [(trial["redXloc"],trial["redYloc"],'R'),(trial["purpleXloc"],trial["purpleYloc"],'P')]
        #     print(chars)
        # except:
        #     # find target in legal moves to get the tile that they move to
        #     x,y = get_target_loc(trial['target'], trial['legalMoves'])
        #     if trial["target"]=="box":
        #         # move out of the way of the box
        #         x,y = x - 1, y + 2
        #         if (chars[otherplayerid][0]==x and chars[otherplayerid][1]==y):
        #             x,y = x + 1, y + 2

        #     # move the corresponding character to their new location
        #     if trial['agent']=="red":
        #         chars[0]=(x,y,'R')
        #     else:
        #         chars[1]=(x,y,'P')
                    
            # # print map current status
            # veglist = get_items_from_string(trial["farmItems"])
            # print_mapstr(veglist, chars)
    
    
