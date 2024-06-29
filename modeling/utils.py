# utils

try:
    import pathfindingpy
except:
    import modeling.pathfindingpy as pathfindingpy

bfs = pathfindingpy.bfs.BreadthFirstFinder()


# Get the walking path between two entities a and b. We need to know the game state to determine if there are any obstacles.
def getPath(state, currentplayer, destination):
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
        destination["loc"]["x"],
        destination["loc"]["y"],
        grid,
    )
    return path


# Given two dicts that have a "loc":{"x":_, "y":_ } property, find the distance from the second to the first
# this does not take collisions into account
def getManhattanDistance(a, b):
    return abs(b["loc"]["x"] - a["loc"]["x"]) + abs(b["loc"]["y"] - a["loc"]["y"])


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
    return map;


# fmt: on
