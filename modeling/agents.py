# imports
from random import randint
import numpy as np
import random
import datetime # for limiting calculation to wall clock time
from math import log, sqrt
import copy
try:
    from utils import *
except:
    from modeling.utils import *
import shortuuid

class RandomPolicy(object):
    
    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()
        self.states = []
        self.agent_type="random"
        self.identity = kwargs.get('color','red') # to be consistent with MCTS
        self.policy = kwargs.get('policy','random') # random is as random does
        self.seed = kwargs.get('seed',717)
        random.seed(self.seed)
        self.rewards = {}
        self.plays = {}
        
    # Take a game state and append it to the history
    def update(self,state):
        self.states.append(state)
        
    # calculates best move and returns it
    def choose_action(self):
        state = self.states[-1]
        legal = state.legal_actions()
        
        if legal == []:
            raise Exception("This shouldn't happen. When player has no moves, legal_actions still has one entry {'name':'none', 'color':player['color'], 'loc':player['loc']}")
        if len(legal)==1:
            return legal[0] # This would happen if the player had no moves, they'd auto choose the "none" action and skip their turn at no cost.
        else:
            return random.choice(legal) # Actual decision policy. Random!

# more agents:
# heuristic policies like
# nearest neighbor (any color)
# nearest neighbor (own color preference)
# nearest neighbor (other color preference)
class NearestNeighborAgent(object):

    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()
        self.states = []
        # seconds = kwargs.get('time',30)
        # self.calculation_time = datetime.timedelta(seconds=seconds)

        self.agent_type="nearestneighbor"
        # TODO: multiple types of agents given argument keywords, e.g., preference for own color is a variation of NN
        self.policy = kwargs.get('policy','nn-colorblind') # initselfish, or selfish or nn-true
        self.identity = kwargs.get('color','red') # default color red if not specified in args
        self.rewards = {}
        self.plays = {}

    # Take a game state and append it to the history
    def update(self,state):
        self.states.append(state)
        
    # calculate best move according to nearest neighbor policy
    def choose_action(self):
        state = self.states[-1]
        legal = state.legal_actions()
        # print(legal)
        
        # IMPORTANT! NEEDS TO CHOOSE RANDOMLY AMONGST EQUALLY GOOD OPTIONS >:(

        action=legal[0]
        if legal == []:
            raise Exception("This shouldn't happen. When player has no moves, legal_actions still has one entry {'name':'none', 'color':player['color'], 'loc':player['loc']}")
        if len(legal)==1:
            action=legal[0] # This would happen if the player had no moves, they'd auto choose the "none" action and skip their turn at no cost.
        else:
            # Choose a move using the heuristic policy
            myplayer = state.redplayer if self.identity=="red" else state.purpleplayer
            pillow_a = [x for x in legal if x['type']=='pillow'][0]
            nonpillow_as = [x for x in legal if x['type']!='pillow']
            # sorted_legal = sorted(legal, key=lambda x: getManhattanDistance(myplayer,x))
            # nonpillow_legal = sorted_legal
            # shortest_dist = getManhattanDistance(myplayer,sorted_legal[1]) # Closest option has this distance, and there might be others with the same

            if self.policy=="nn-colorblind":
                # if there is still space in my backpack, pick up a vegetable (even if i'm closer to the box)
                legalveg = [x for x in nonpillow_as if x["type"]=="veggie"] # so not looking at pillow option
                if len(legalveg)==0:
                    # no legal veg, so my bp must be full
                    action=self.select_any_shortest(myplayer,nonpillow_as) # just choose the non-pillow available legal action
                else:
                    action=self.select_any_shortest(myplayer,legalveg) # choose closest veg
            elif self.policy=="nn-initselfish":
                legalveg = [x for x in legal if x["type"]=="veggie"] # so not looking at pillow option
                legalOwnVeg = [x for x in legalveg if x["color"]==self.identity] # only veg of own color
                if len(legalOwnVeg)>0: # if we do have our own veg on the farm, pick up the closest one
                    action = self.select_any_shortest(myplayer,legalOwnVeg)
                else: # None of our own veg; any of the partner's veg left?
                    if len(legalveg)>0:
                        action=self.select_any_shortest(myplayer,legalveg) # yes, lets go pick it up for them
                    else:
                        action=self.select_any_shortest(myplayer,nonpillow_as) # alright folks must be our backpack is full so go box
            elif self.policy=="nn-selfish":
                legalveg = [x for x in legal if x["type"]=="veggie"] # so not looking at pillow option
                legalOwnVeg = [x for x in legalveg if x["color"]==self.identity] # only veg of own color
                if len(legalOwnVeg)==0:
                    # is box an option? try that first
                    boxaction = [x for x in legal if x["type"]=="box"]
                    if len(boxaction)==0:
                        # can't go to box but we aren't gonna go pick up some other veg lol just sleep
                        action=self.select_any_shortest(myplayer,legal) # pillow baby
                    else: # but if box is an option do do that before you sleep for the rest of the game lol
                        action=boxaction[0]
                else: # yay let's pick up our closest own veg
                    action=self.select_any_shortest(myplayer,legalOwnVeg)
            elif self.policy=="nn-true": # this one literally picks whatever is closest be it veggie or box (even if bp not full)
                # after sorting, first object is always pillow
                action = self.select_any_shortest(myplayer,nonpillow_as) # pick nearest legal action that is not the self lol 
        return action

    def select_any_shortest(self,player,actions):
        # what is the closest action of the list we were given?
        sorted_as = sorted(actions, key=lambda x: getManhattanDistance(player,x))
        shortest_dist = getManhattanDistance(player,sorted_as[0]) # Closest option has this distance, and there might be others with the same

        # if there are multiple closest actions, randomly choose between them
        return random.choice([x for x in sorted_as if getManhattanDistance(player,x)==shortest_dist])