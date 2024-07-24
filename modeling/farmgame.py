from __future__ import annotations
from collections import Counter
from enum import Enum
from typing import NamedTuple
import copy
import csv
import random
import utils

class ActionType(str, Enum):
    none = "none"
    pillow = "pillow"
    timeout = "timeout"
    box = "box"
    veggie = "veggie"

class Action():
    def __init__(self, name: str, type: ActionType, color: str, loc: dict, id: str) -> None:
        self.name = name
        self.type = type
        self.color = color
        self.loc = loc
        self.id = id
    
    def get_target(self) -> str:
        if self.type == ActionType.veggie:
            return "redVeg" if self.color == "red" else "purpleVeg"
        return self.type
    
    def get_category(self, player_color: str) -> str:
        if self.type == ActionType.veggie:
            return "ownVeg" if player_color == self.color else "otherVeg"
        return self.type

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        return isinstance(other, Action) and other.id == self.id
    
    def __str__(self) -> str:
        return f"{self.id}({self.loc['x']},{self.loc['y']})"

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
        box_config = config.get("farmbox", {})
        self.farmbox = self.create_farmbox(
            box_config.get("loc", {"x": 16, "y": 5}),
            box_config.get("boxcontents", [])
        )  # default starts as empty box
        self.stepcost = config.get(
            "stepcost"
        )  # 1 # but it could be twoooooo # config.stepcost
        self.pillowcost = config.get("pillowcost")
        self.map = (
            utils.getMap()
        )  # map # GLOBAL VAR same map of collisions for all games #config.get('map')
        self.turn = config.get("turn", 0)  # self.players[0]
        self.trial = config.get("trial", 0)  # game starts at trial 0

        # condition info
        self.resourceCond = config.get("condition")["resourceCond"]
        self.costCond = config.get("condition")["costCond"]
        self.visibilityCond = config.get("condition")["visibilityCond"]

    def get_cost(self, action: Action) -> float:
        # no cost if no actions were available to the player
        if action.type == ActionType.none:
            return 0

        # fixed cost if voluntarily passing
        if action.type == ActionType.pillow or action.type == ActionType.timeout:
            return self.pillowcost

        # whose turn is it?
        currentplayer = self.whose_turn()

        # player moves to location. decrease energy by steps taken.
        # find shortest path with bfs, use that step length to decrement energy
        path = utils.getPath(self, currentplayer, action)
        n_steps = len(path) - 1
        if utils.is_in_line(currentplayer["loc"], self.other_player()["loc"], action.loc):
            # Add 2 sidesteps if the other player is in the way. Somehow getPath doesn't cover this.
            n_steps += 2

        # decrease energy for move out of the way
        if action.type == ActionType.box:
            statuses = Counter(item.status for item in self.items)
            if "farm" in statuses or statuses["backpack"] > len(currentplayer["backpack"]["contents"]):
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
        if action.type == ActionType.none:
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
        if action.type == ActionType.pillow:
            new_state.nextturn()
            return new_state

        # aha, so the player needs to move! player moves to location.
        # change player's location to action target location.
        currentplayer["loc"] = action.loc

        # if item, add to backpack.
        if action.type == ActionType.veggie:
            # FIND VEGGIE IN ITEMS rather than changing action directly
            veg = next(
                (item for item in new_state.items if item.id == action.id), None
            )
            veg.status = "backpack"
            currentplayer["backpack"]["contents"].append(action)
            if Transition(self, action).is_helping():
                currentplayer["has_helped"] = True

        # if box, add backpack contents to box. increment score.
        if action.type == ActionType.box:
            for _ in range(len(currentplayer["backpack"]["contents"])):
                veg = currentplayer["backpack"]["contents"].pop()
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
            if new_state.is_done():
                new_state.redplayer["bonuspoints"] = new_state.reward("red")
                new_state.purpleplayer["bonuspoints"] = new_state.reward("purple")
                return new_state
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
    
    def is_done(self):
        return all(item.status == "box" for item in self.items)

    # TODO: There is lots of room for different reward functions
    def reward(self, playercolor: str):
        if playercolor == "red":
            relevantplayer = self.redplayer
        elif playercolor == "purple":
            relevantplayer = self.purpleplayer
        else:
            print("EROR")

        # currentplayer = state.players[state.turn]
        reward = 0
        # is the game over? set done to true, give bonus points
        if self.is_done():
            # print(playercolor + " player's score is " + str(relevantplayer['score']) + " and energy is " + str(relevantplayer['energy']))
            relevantplayer["bonuspoints"] = (
                relevantplayer["score"] * relevantplayer["energy"]
            )
            # otherplayer.bonuspoints = otherplayer.score * otherplayer.energy
            reward = relevantplayer["bonuspoints"]
        # else:
        #     reward = relevantplayer.score #just how many items they have delivered as they go along

        return reward

    def whose_turn(self):
        return self.players[self.turn]
    
    def other_player(self):
        return self.players[1 - self.turn]

    def legal_actions(self) -> list[Action]:
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
            action_list.append(self.create_pillow("pillow", player["color"], player["loc"]))

        # This is the case where there are actually no moves left for the agent.  They're forced to just stay in place but there is no cost (unlike pillow)
        if len(action_list) == 0 and not all(i.status == "box" for i in self.items):
            action_list.append(self.create_pillow("none", player["color"], player["loc"]))

        return action_list

    @staticmethod
    def create_player(config):
        # purple starts at 'x':3, 'y':16
        # red starts at 'x':2, 'y':15
        player = {}
        player["loc"] = config.get("loc")
        player["name"] = config.get("name")
        player["type"] = "player"
        player["color"] = config.get("name")
        player["capacity"] = config.get("capacity")
        player["contents"] = config.get("contents", [])
        player["backpack"] = Farm.create_backpack(
            {
                "name": config.get("name"),
                "capacity": config.get("capacity"),
                "contents": config.get("contents", []),
            }
        )  # default backpacksettings
        player["score"] = config.get("score", 0)
        player["energy"] = config.get("energy", 100)
        player["bonuspoints"] = config.get("bonuspoints", 0)
        player["has_helped"] = config.get("has_helped", False)
        return player

    @staticmethod
    def create_farmbox(location: dict[str, int], contents=[]) -> Action:
        farmbox = Action("box", ActionType.box, None, location, "box")
        farmbox.contents = contents
        return farmbox

    @staticmethod
    def create_veggie(name: str, color: str, vegstr: str, status="farm") -> Action:
        veggie = Action(name, ActionType.veggie, color, Farm.extract_location(vegstr), vegstr.split("(")[0])
        veggie.status = status
        return veggie

    @staticmethod
    def create_backpack(config):
        backpack = {}
        backpack["name"] = config.get("name")
        backpack["type"] = "backpack"
        backpack["capacity"] = config.get("capacity", 4)
        backpack["contents"] = config.get("contents", [])
        return backpack

    @staticmethod
    def create_pillow(name: str, color: str, loc: dict[str, int]) -> Action:
        type = ActionType.none if name == "none" else ActionType.pillow
        pillow = Action(name, type, color, loc, color + name)
        return pillow

    @staticmethod
    def extract_location(item: str) -> dict[str, int]:
        x, y = item.split("(")[-1].strip(")").split(",")
        return {"x": int(x), "y": int(y)}
    
    @staticmethod
    def create_item(vegstr: str) -> Action:
        # veggie str looks something like: 'Tomato00(8,7)' or 'Strawberry00(7,7)'
        name = vegstr.split("0")[0].lower()
        color = "red" if name == "tomato" or name == "strawberry" else "purple"
        return Farm.create_veggie(name, color, vegstr)

    def create_items(self, layer: str) -> list[Action]:  # twelve possible layers, "Items00" thru "Items11"

        # configure how to get list of veggies from a given starting setup (one of the twelve object layers)
        fname = "config/objectLayers.csv"
        objectlayers = {}

        with open(fname, "r") as data:
            for line in csv.DictReader(data):
                layername = line["objectLayer"]
                farmitems = line["farmItems"].strip("']['").split(" ")
                # print(layername)
                objectlayers[layername] = farmitems

        # twelve possible layers, "Items00" thru "Items11"
        return [self.create_item(vegstr) for vegstr in objectlayers[layer]]

    def __iter__(self):
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

        for i in range(len(props)):
            yield immutify(props[i])

    @staticmethod
    def unpack(tupstate):
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

    def next_state(self) -> Farm:
        return self.state.take_action(self.action, inplace=False)

    def is_helping(self, target_player: str|dict = None) -> bool:
        if not self.action:
            return False
        if target_player:
            target_color = target_player["color"] if isinstance(target_player, dict) else target_player
            if target_color != self.state.whose_turn()["color"]:
                # a player can't be helping if it isn't their turn
                return False
        return self.action.color == self.state.other_player()["color"]
    
    def __str__(self) -> str:
        return f"{self.state.trial:>2}. {self.state.whose_turn()['color']} picks {self.action}"

Game = list[Transition]
Session = list[Game]

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
