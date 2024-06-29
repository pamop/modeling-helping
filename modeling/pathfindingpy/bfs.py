# breadth first search adapted to python from js 
# by pam osborn popp [email: pamosbornpopp@gmail.com]
# original js source: https://github.com/qiao/PathFinding.js

from operator import truediv
from .util import *

class BreadthFirstFinder:
    def __init__(self, opt={}):
        self.opt = opt

    def findpath(self, startX, startY, endX, endY, grid):
        openlist=[]
        startnode = grid.getnodeat(startX, startY)
        endnode = grid.getnodeat(endX, endY)
        
        # push start pos into queue
        openlist.append(startnode)
        startnode.opened=True

        while len(openlist)>0:
            # take the front node from the queue
            node = openlist.pop(0)
            node.closed=True

            if node == endnode:
                return backtrace(endnode) # method from util.py
            
            neighbors = grid.getneighbors(node)
            for neighbor in neighbors:
                if hasattr(neighbor, 'closed') or hasattr(neighbor, 'opened'): # EDIT: if neighbor HAS either of these properties, then skip it (it has already been inspected)
                    continue
                else:
                    openlist.append(neighbor)
                    neighbor.opened=True
                    neighbor.parent=node
        
        # else faaaail
        return []