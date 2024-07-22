# pathfinding adapted to python from js 
# by pam osborn popp [email: pamosbornpopp@gmail.com]
# original js source: https://github.com/qiao/PathFinding.js

from .node import Node

def backtrace(node):
    path = [[node.x, node.y]]
    while hasattr(node,"parent"):
        node = node.parent
        path.append([node.x,node.y])

    return path[::-1] # reverse order to go forward!

