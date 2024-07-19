from __future__ import annotations
import copy

# try:
#     import pathfindingpy
# except:
#     import modeling.pathfindingpy as pathfindingpy
import csv
import random
from typing import Any, List, NamedTuple

class Action():
    def __init__(self, name: str, type: str, color: str, loc: dict, id: str) -> None:
        self.name = name
        self.type = type
        self.color = color
        self.loc = loc
        self.id = id

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        return isinstance(other, Action) and other.id == self.id
    
    def __str__(self) -> str:
        return self.id

try:
    from utils import *
except:
    from modeling.utils import *

# state space
# state is an object with various features that define the current world. a snapshot of the current game
# - location and identities of agents
# - current energy level of agents
# - location and identities of items
# - backpack size, contents
# - farmbox contents
# - turn (who makes next decision AND numerical count of moves taken so far)
# - timestamp
# - anything else...????
class Farm:
    # NOTE: anything you add to init, must be added to config in deep_copy method to ensure entire state info is copied
    def __init__(self, config):
        self.redplayer = self.create_player(
            config.get("redplayer")
        )  # Player({'name':'red','x':2, 'y':15,'backpack':Backpack()})
        self.purpleplayer = self.create_player(
            config.get("purpleplayer")
        )  # Player({'name':'purple','x':3, 'y':16,'backpack':Backpack()})
        self.redfirst = config.get("redfirst")
        self.players = (
            [self.redplayer, self.purpleplayer]
            if config.get("redfirst")
            else [self.purpleplayer, self.redplayer]
        )  # config.players #[] # TODO random who starts first
        self.playersDict = {"red": self.redplayer, "purple": self.purpleplayer}
        temp = config.get("items")
        if (
            type(temp) == str
        ):  # we have been given the name of the item layer to generate items with
            self.objectLayer = temp
            self.items = self.create_items(temp)
        else:  # we have been given the list of items itself
            self.objectLayer = "uhhh"
            self.items = temp
        self.farmbox = self.create_farmbox(
            config.get("farmbox", {})
        )  # default starts as empty box
        self.stepcost = config.get(
            "stepcost"
        )  # 1 # but it could be twoooooo # config.stepcost
        self.pillowcost = config.get("pillowcost")
        self.map = (
            getMap()
        )  # map # GLOBAL VAR same map of collisions for all games #config.get('map')
        self.turn = config.get("turn", 0)  # self.players[0]
        self.trial = 0  # game starts at trial 0

        # condition info
        self.resourceCond = config.get("condition")["resourceCond"]
        self.costCond = config.get("condition")["costCond"]
        self.visibilityCond = config.get("condition")["visibilityCond"]

    def get_cost(self, action: Action) -> float:
        # no cost if no actions were available to the player
        if action.type == "none":
            return 0

        # fixed cost if voluntarily passing
        if action.type == "pillow":
            return self.pillowcost

        # whose turn is it?
        currentplayer = self.players[self.turn]

        # player moves to location. decrease energy by steps taken.
        # find shortest path with bfs, use that step length to decrement energy
        path = getPath(self, currentplayer, action)
        n_steps = len(path)

        # decrease energy for move out of the way
        if action.type == "box":
            n_steps += 3 # three because moving 1,2 away
        return n_steps * self.stepcost

    def take_action(self, action: Action, inplace=True) -> Farm:
        if inplace:
            new_state = self
        else:
            new_state = copy.deepcopy(
                self
            )  # does the native python copy.deepcopy method work here, or do i need to customize in __deepcopy__?

        # what does the selected action do the player locations, item locations, and player scores + energy?

        # no costs and nothing happens
        if action.type == "none":
            new_state.nextturn()
            return new_state

        # from here we need to know whose turn it is to update the state properly.
        playercolor = new_state.players[new_state.turn]["name"]
        if playercolor == "red":
            currentplayer = new_state.redplayer
            otherplayer = new_state.purpleplayer
        else:
            currentplayer = new_state.purpleplayer
            otherplayer = new_state.redplayer

        # decrease energy for the action
        currentplayer["energy"] = max(0, currentplayer["energy"] - new_state.get_cost(action))

        # if action is pillow, no movement, no encounter, just small energy cost and move on.
        if action.type == "pillow":
            new_state.nextturn()
            return new_state

        # aha, so the player needs to move! player moves to location.
        # change player's location to action target location.
        currentplayer["loc"] = action.loc

        # if item, add to backpack.
        if action.type == "veggie":
            # FIND VEGGIE IN ITEMS rather than changing action directly
            veg = next(
                (item for item in new_state.items if item.id == action.id), None
            )
            veg.status = "backpack"
            veg.loc = None
            currentplayer["backpack"]["contents"].append(veg)
            if veg.color != currentplayer["color"]:
                currentplayer["has_helped"] = True

        # if box, add backpack contents to box. increment score.
        if action.type == "box":
            for _ in range(len(currentplayer["backpack"]["contents"])):
                veg = currentplayer["backpack"]["contents"].pop(0)
                veg.status = "box"

                # print(currentplayer["name"] + " deposits " + veg["id"])

                # update status of veg in items list as well
                veg_item = next(
                    (item for item in new_state.items if item.id == veg.id), None
                )
                veg_item.status = "box"

                # add the veg to the farmbox
                new_state.farmbox.contents.append(veg)
                if veg.color == currentplayer["name"]:
                    currentplayer["score"] += 1
                elif veg.color == otherplayer["name"]:
                    otherplayer["score"] += 1
                else:
                    print("The veggie is neither red nor purple?")
            # move out of the way of the box
            pos = currentplayer["loc"]
            newpos = {"x": pos["x"] - 1, "y": pos["y"] + 2}
            if newpos == otherplayer["loc"]:
                newpos = {"x": pos["x"] + 1, "y": pos["y"] + 2}
            currentplayer["loc"] = newpos

        new_state.nextturn()
        return new_state

    def opponent_has_helped(self, color: str) -> bool:
        opponent = self.redplayer if color == "red" else self.purpleplayer
        return opponent["has_helped"]

    def nextturn(self) -> None:
        self.trial += 1
        self.turn += 1
        if self.turn > 1:
            self.turn = 0
        return

    # TODO: There is lots of room for different reward functions
    def reward(self, playercolor: str):
        if playercolor == "red":
            relevantplayer = self.redplayer
        elif playercolor == "purple":
            relevantplayer = self.purpleplayer
        else:
            print("EROR")

        state = self
        # currentplayer = state.players[state.turn]
        reward = 0
        done = False
        # is the game over? set done to true, give bonus points
        if all(i.status == "box" for i in state.items):
            done = True
            # print(playercolor + " player's score is " + str(relevantplayer['score']) + " and energy is " + str(relevantplayer['energy']))
            relevantplayer["bonuspoints"] = (
                relevantplayer["score"] * relevantplayer["energy"]
            )
            # otherplayer.bonuspoints = otherplayer.score * otherplayer.energy
            reward = relevantplayer["bonuspoints"]
        # else:
        #     reward = relevantplayer.score #just how many items they have delivered as they go along

        return reward, done

    def legal_actions(self) -> List[Action]:
        action_list = []
        player = self.players[self.turn]
        # bag full
        if len(player["backpack"]["contents"]) >= player["backpack"]["capacity"]:
            # append box and nothing else
            action_list.append(self.farmbox)
        elif (
            len(player["backpack"]["contents"]) > 0
            and len(player["backpack"]["contents"]) < player["backpack"]["capacity"]
        ):
            # non-empty bag, so append box and remaining items
            action_list = [i for i in self.items if i.status == "farm"]
            action_list.append(self.farmbox)
        else:
            # empty bag
            action_list = [i for i in self.items if i.status == "farm"]

        if len(action_list) != 0:
            # pillow is only an option if you have other options
            # if game is not done, and no other moves, must pass turn (aka pillow)
            # create pillow new each time because player location changes
            action_list.append(
                self.create_pillow(
                    {"name": "pillow", "color": player["color"], "loc": player["loc"]}
                )
            )

        # This is the case where there are actually no moves left for the agent.  They're forced to just stay in place but there is no cost (unlike pillow)
        if len(action_list) == 0 and not all(i.status == "box" for i in self.items):
            action_list.append(
                self.create_pillow(
                    {"name": "none", "color": player["color"], "loc": player["loc"]}
                )
            )

        # if game is not done, and no other moves, can pass turn
        # if (len(action_list)==0 and not all(i['status']=="box" for i in self.items)):
        #     # action_list.append({'name':'pass','color':player['color'], 'loc':player['loc'], 'id':'pass','type':'pass'})
        #     action_list.append(self.create_pillow({'name':'pillow', 'color':player['color'], 'loc':player['loc']}))

        return action_list

    def create_player(self, config):
        # purple starts at 'x':3, 'y':16
        # red starts at 'x':2, 'y':15
        player = {}
        player["loc"] = config.get("loc")
        player["name"] = config.get("name")
        player["type"] = "player"
        player["color"] = config.get("name")
        player["capacity"] = config.get("capacity")
        player["contents"] = config.get("contents", [])
        player["backpack"] = self.create_backpack(
            {
                "name": config.get("name"),
                "capacity": config.get("capacity"),
                "contents": config.get("contents", []),
            }
        )  # default backpacksettings
        player["score"] = 0
        player["energy"] = 100
        player["bonuspoints"] = 0
        player["has_helped"] = False
        return player

    def create_farmbox(self, config) -> Action:
        farmbox = Action("box", "box", None, config.get("loc", {"x": 16, "y": 5}), "box")
        farmbox.contents = config.get("boxcontents", [])
        return farmbox

    def create_veggie(self, config) -> Action:
        veggie = Action(config.get("name"), "veggie", config.get("color"), config.get("loc"), config.get("id"))
        veggie.status = config.get("status", "farm")
        return veggie

    def create_backpack(self, config):
        backpack = {}
        backpack["name"] = config.get("name")
        backpack["type"] = "backpack"
        backpack["capacity"] = config.get("capacity", 4)
        backpack["contents"] = config.get("contents", [])
        return backpack

    def create_pillow(self, config) -> Action:
        pillow = Action(config.get("name"),  config.get("name"), config.get("color"), config.get("loc"), config.get("color") + config.get("name"))
        return pillow

    def create_items(self, layer: str) -> List[Action]:  # twelve possible layers, "Items00" thru "Items11"

        # configure how to get list of veggies from a given starting setup (one of the twelve object layers)
        fname = "config/objectLayers.csv"
        objectlayers = {}

        with open(fname, "r") as data:
            for line in csv.DictReader(data):
                layername = line["objectLayer"]
                farmitems = line["farmItems"].strip("']['").split(" ")
                # print(layername)
                objectlayers[layername] = farmitems

        veggies = []
        # twelve possible layers, "Items00" thru "Items11"
        for vegstr in objectlayers[layer]:
            # veggie str looks something like: 'Tomato00(8,7)' or 'Strawberry00(7,7)'
            name = vegstr.split("0")[0].lower()
            x, y = vegstr.split("(")[-1].split("(")[-1].strip(")").split(",")
            color = "red" if name == "tomato" or name == "strawberry" else "purple"
            vegconfig = {
                "loc": {"x": int(x), "y": int(y)},
                "name": name,
                "color": color,
                "id": vegstr,
            }
            veggies.append(self.create_veggie(vegconfig))
        return veggies

    def __iter__(self):
        # properties = [
        #     tuple(self.redplayer.items()),      #0  # convert dicts to tuples with items() method so retain all info
        #     tuple(self.purpleplayer.items()),   #1
        #     self.redfirst,       #2
        #     tuple(self.items.items()),          #3
        #     tuple(self.farmbox.items()),        #4
        #     self.stepcost,       #5
        #     self.turn            #6
        #     ]
        # for i in range(len(properties)):
        #     yield properties[i]
        state = copy.deepcopy(
            self
        )  # otherwise it turns the items themselves into tuples!
        props = [
            state.redplayer,
            state.purpleplayer,
            state.redfirst,
            state.items,  # argh this is a list
            state.farmbox,
            state.stepcost,
            state.pillowcost,
            state.turn,
        ]
        # proptuple = immutify_dict(props)

        for i in range(len(props)):
            yield immutify(props[i])

    # this method doesn't use self but can be accessed from any farm obj
    def unpack(self, tupstate):
        # given a tuple of the farm, unpack it to create a farm object
        config = {
            "redplayer": demutify(tupstate[0]),
            "purpleplayer": demutify(tupstate[1]),
            "redfirst": tupstate[2],
            "items": demutify(tupstate[3]),
            "farmbox": demutify(tupstate[4]),
            "stepcost": tupstate[5],
            "pillowcost": tupstate[6],
            "turn": tupstate[7],
        }
        # config = demutify_dict(tupstate)
        # print(config)
        return Farm(config)

    # def __str__(self):
    #     return "tbd"

    def print_farm(self):
        print("todo")
        return

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        # print(hash(tuple(self)))
        shash = hash(tuple(self))
        # shashkey = str(shash)
        # # with shelve.open('farmstatehash') as shelf:
        # #     if not shashkey in shelf:
        # #         # we need to store this state as it has never been hashed before
        # #         shelf[shashkey]= self #tuple(self) # CAN I STORE THE ACTUAL OBJECT INSTEAD OF TUPSTATE???
        # farmstatehash[shashkey]=self

        return shash  # todo: use better hash library?

class Transition(NamedTuple):
    state: Farm
    action: Action

Game = List[Transition]
Session = List[Game]

# # global
# def getstatefromhash(shash):
#     return farmstatehash[str(shash)]
#     # def __deepcopy__(self):
#     #     # return a full copy of the current game state (but a new object in memory)
#     #     config = {"players": self.players,
#     #             "items": self.items,
#     #             "farmbox": self.farmbox,
#     #             "turn": self.turn
#     #             }
#     #     new_state = Farm(config)


def unpack_farm(tupstate):
    # given a tuple of the farm, unpack it to create a farm object
    # print('\nunpacking farm!')
    # print(tupstate[0])
    # print(demutify(tupstate[0]))
    # all good up to here
    config = {
        "redplayer": demutify(tupstate[0]),
        "purpleplayer": demutify(tupstate[1]),
        "redfirst": tupstate[2],
        "items": demutify(tupstate[3]),
        "farmbox": demutify(tupstate[4]),
        "stepcost": tupstate[5],
        "pillocost": tupstate[6],
        "turn": tupstate[7],
    }
    # config = demutify_dict(tupstate)
    # print(config)
    return Farm(config)


def immutify(d):
    if type(d) == list:
        for i in range(len(d)):
            if type(d[i]) == dict:
                d[i] = immutify(d[i])
        return tuple(d)

    if type(d) != dict:
        return d

    for key, val in d.items():
        if type(val) == dict or type(val) == list:
            d[key] = immutify(val)

    # if no nested dictionaries, we are good
    return tuple(d.items())


def demutify(d):
    # if type(d)==str or type(d)==int or type(d)==float:
    #     return d
    if type(d) == list:
        return [demutify(i) for i in d]

    if type(d) != tuple:
        return d

    if d == ():
        return []

    try:
        d = dict(d)
        for key, val in d.items():
            if type(val) == tuple:
                d[key] = demutify(val)
    except:
        d = list(d)

        if type(d) == list:
            return [demutify(i) for i in d]

    # if no nested tuples, we're good
    return d


def configure_game(
    layer="Items00",
    resourceCond="even",
    costCond="low",
    visibilityCond="full",
    redFirst=True,
):
    itemlayer = layer
    condition = {
        "resourceCond": resourceCond,  #'even', # or "uneven"
        "costCond": costCond,  #'low', # or "high"
        "visibilityCond": visibilityCond,
    }  #'full'} # or "self"

    # generate the game config based on the setup
    if condition["resourceCond"] == "even":
        rbp, pbp = 4, 4
    elif condition["resourceCond"] == "unevenRed":
        rbp, pbp = 5, 3
    elif condition["resourceCond"] == "unevenPurple":
        rbp, pbp = 3, 5
    else:
        if random.random() < 0.5:
            rbp, pbp = 5, 3
        else:
            rbp, pbp = 3, 5

    config = {
        "redplayer": {
            "name": "red",
            "loc": {"x": 2, "y": 15},
            "capacity": rbp,
            "contents": [],
        },
        "purpleplayer": {"name": "purple", "loc": {"x": 3, "y": 16}, "capacity": pbp},
        "redfirst": redFirst,  # if random.random()<0.5 else False,
        "items": layer,
        "stepcost": 1 if condition["costCond"] == "low" else 2,
        "pillowcost": 5,  # If pillow cost ever changes, this would have to be adjustable, but i don't plan on changing it rn
        "condition": condition,
    }

    return Farm(config)


# # GLOBAL COLLISIONS MAP (BEFORE UNWALKABLE LOCATION OF PARTNER IS ADDED)
# #       0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19
# map = [[1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], # 0
#        [1., 1., 0., 0., 0., 0., 1., 1., 1., 1., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 1
#        [1., 0., 0., 0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 2
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 3
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1.], # 4
#        [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 0., 1., 1., 1.], # 5
#        [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 6
#        [1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 7
#        [1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 8
#        [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 9
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 10
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.], # 11
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1.], # 12
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1.], # 13
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1.], # 14
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1.], # 15
#        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1.], # 16
#        [1., 1., 0., 0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1.], # 17
#        [1., 1., 1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1.], # 18
#        [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]] # 19
