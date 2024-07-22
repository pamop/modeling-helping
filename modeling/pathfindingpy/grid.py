# pathfinding adapted to python from js 
# by pam osborn popp [email: pamosbornpopp@gmail.com]
# original js source: https://github.com/qiao/PathFinding.js

from .node import Node
# import numpy as np
import copy

class Grid:
    def __init__(self, width_or_matrix, height=0, matrix=[]):
        if isinstance(width_or_matrix, int):
            self.width = width_or_matrix
            self.height = height
            self.matrix = [[0] * self.width] * self.height
        else: # input is just a matrix
            self.width = len(width_or_matrix[0])
            self.height = len(width_or_matrix)
            self.matrix = width_or_matrix

        self.nodes = self.buildnodes(self.width, self.height, self.matrix)

    def buildnodes(self, width, height, matrix):
        nodes = [0] * height
        for i in range(height):
            nodes[i] = [0] * width
            for j in range(width):
                nodes[i][j] = Node(j,i)

        if matrix==[]:
            return nodes
        
        if (len(matrix) != height) or (len(matrix[0]) != width):
            print("Uh oh! Matrix size doesn't fit! Errrorrrr")
        
        for i in range(len(nodes)):
            for j in range(len(nodes[0])):
                if matrix[i][j]: # if this value is 1, means tile is obstructed
                    nodes[i][j].walkable = False
                else: # if value is 0, false, or null, then we can walk on it
                    nodes[i][j].walkable = True

        return nodes

    def getmatrix(self):
        return [[int(not node.walkable) for node in noderow] for noderow in self.nodes]

    def getnodeat(self, x, y):
        return self.nodes[y][x]

    def iswalkableat(self, x, y):
        return self.isinside(x, y) and self.nodes[y][x].walkable
    
    def isinside(self, x, y):
        return (x>=0 and x<self.width) and (y>=0 and y<self.height)

    def setwalkableat(self, x, y, walkable):
        self.nodes[y][x].walkable = walkable
        return
    
    def getneighbors(self, node):
        x=node.x
        y=node.y
        neighbors = []
        s0 = False
        s1 = False
        s2 = False
        s3 = False
        nodes = self.nodes

        # UP
        if self.iswalkableat(x, y-1):
            neighbors.append(nodes[y-1][x])
            s0 = True

        # RIGHT
        if self.iswalkableat(x+1, y):
            neighbors.append(nodes[y][x+1])
            s1 = True

        # DOWN
        if self.iswalkableat(x, y+1):
            neighbors.append(nodes[y+1][x])
            s2 = True

        # LEFT
        if self.iswalkableat(x-1, y):
            neighbors.append(nodes[y][x-1])
            s3 = True
        
        return neighbors

    def clone(self):
        return copy.deepcopy(self)

