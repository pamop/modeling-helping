# pathfinding adapted to python from js 
# by pam osborn popp [email: pamosbornpopp@gmail.com]
# original js source: https://github.com/qiao/PathFinding.js

class Node:
    def __init__(self, x, y, walkable=True):
        self.x = x
        self.y = y
        self.walkable = walkable
    
    def __str__(self): 
        return "NODE: x=%s, y=%s, walkable=%s" % (self.x, self.y, "yes" if self.walkable else "no") 
