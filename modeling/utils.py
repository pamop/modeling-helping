# utils

import math
import pathfindingpy

bfs = pathfindingpy.bfs.BreadthFirstFinder()


# Get the walking path between two entities a and b. We need to know the game state to determine if there are any obstacles.
def getPath(state, currentplayer: dict, destination_action):
    # the default map of the game tells us all the environment collisions
    grid = pathfindingpy.Grid(
        state.map
    )  # the default map, now make the other player's location unwalkable

    # get ref to other player so can mark their loc as an obstacle
    otherplayer = (
        state.redplayer if currentplayer["color"] == "red" else state.purpleplayer
    )
    grid.setwalkableat(otherplayer["loc"]["x"], otherplayer["loc"]["y"], False)

    # get shortest path between player and destination given this grid
    path = bfs.findpath(
        currentplayer["loc"]["x"],
        currentplayer["loc"]["y"],
        destination_action.loc["x"],
        destination_action.loc["y"],
        grid,
    )
    return path


# Given two dicts that have a "loc":{"x":_, "y":_ } property, find the distance from the second to the first
# this does not take collisions into account
def getManhattanDistance(a, b):
    return abs(b["x"] - a["x"]) + abs(b["y"] - a["y"])


def is_in_line(origin: dict, block: dict, dest: dict,) -> bool:
    if origin["x"] == dest["x"] and origin["x"] == block["x"]:
        # straight vertical line. Check if the blocking object is in the middle
        block_origin = block["y"] - origin["y"]
        block_dest = block["y"] - dest["y"]
        return block_origin != math.copysign(block_origin, block_dest)
    if origin["y"] == dest["y"] and origin["y"] == block["y"]:
        # straight horizontal line. Check if the blocking object is in the middle
        block_origin = block["x"] - origin["x"]
        block_dest = block["x"] - dest["x"]
        return block_origin != math.copysign(block_origin, block_dest)
    return False


def get_differences(d1: dict | list, d2: dict | list, skip_keys=[], path="") -> list[str]:
    differences = []
    if isinstance(d1, dict):
        for key in d1:
            if key in skip_keys:
                continue
            if isinstance(d1[key], (dict, list)):
                differences.extend(get_differences(d1[key], d2[key], skip_keys, f"{path}/{key}"))
            elif d1[key] != d2[key]:
                differences.append(f"{path}/{key}: {d1[key]} != {d2[key]}")
    else:
        if len(d1) != len(d2):
            differences.append(f"{path} unequal list size: {[str(thing) for thing in d1]} != {[str(thing) for thing in d2]}")
        else:
            for i in range(len(d1)):
                if d1[i] != d2[i]:
                    differences.append(f"{path}/{i}: {d1[i]} != {d2[i]}")
    return differences


def get_player_differences(player1: dict, player2: dict, name: str) -> list[str]:
    differences = get_differences(player1, player2, ["loc"], name)
    if getManhattanDistance(player1["loc"], player2["loc"]) > 1:
        differences.extend(get_differences(player1["loc"], player2["loc"], [], f"{name}/loc"))
    return differences


def get_farm_differences(state1, state2) -> list[str]:
    def list_props(state) -> dict:
        return {
            "farmbox": state.farmbox.contents,
            "items": state.items,
            "redfirst": state.redfirst,
            "pillowcost": state.pillowcost,
            "turn": state.turn,
            "trial": state.trial
        }
    differences = get_differences(list_props(state1), list_props(state2), [], "farm")
    differences.extend(get_player_differences(state1.redplayer, state2.redplayer, "redplayer"))
    differences.extend(get_player_differences(state1.purpleplayer, state2.purpleplayer, "purpleplayer"))
    return differences

# fmt: off
# GLOBAL COLLISIONS MAP (BEFORE UNWALKABLE LOCATION OF PARTNER IS ADDED)
def getMap():
#            0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19
    map =  [[1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], # 0
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
    return map


# fmt: on
