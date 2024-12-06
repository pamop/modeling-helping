# ALL STATES ARE TUPLE FORM
# must be unpacked in farmgame.py for object level methods

# imports
from random import randint
import numpy as np
import random
import datetime # for limiting calculation to wall clock time
from math import log, sqrt
import copy
import shortuuid
try:
    from utils import *
except:
    from modeling.utils import *
# from farmgame import getstatefromhash
# import shelve

# # import state hash dictionary
# # print(hash(tuple(self)))
# def getstatefromhash(shash):
#     with shelve.open('farmstatehash') as shelf:
#         # tupstate = shelf[shash]
#         state = shelf[str(shash)]
#     return state

class MCTS(object):
    
    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()
        self.states = []
        self.tupstates = []
        self.shashes = []
        self.identity = kwargs.get('color','red')
        self.agent_type="mcts"
        self.policy = kwargs.get('policy',"selfish") # altruistic, or collaborative
        seconds = kwargs.get('time',5) # default 5s of simulations
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.nsims=kwargs.get('nsims',1000000) # will stop when first of the two (calc time and nsims) is reached
        self.max_moves = kwargs.get('max_moves')
        self.C = kwargs.get('C', 100)
        self.verbose = kwargs.get('verbose',False) 
        self.rewards = {}
        self.plays = {}
        self.n_random = 0
        self.n_best = 0
        self.farmstatehash = {}
        self.agent_information = {"color":self.identity, "agent_type":self.agent_type,"time":self.calculation_time,"max_moves":self.max_moves,"C":self.C}

        
    # Take a game state and append it to the history
    def update(self,state):
        self.states.append(state)
        self.tupstates.append(tuple(state))
        # print('random', self.n_random, 'best', self.n_best)
        
    # calculates best move and returns it
    def choose_action(self):
        self.max_depth = 0
        #state is a farm object
        state = self.states[-1]
        player = self.identity 
        legal = state.legal_actions() 
        
        if legal == []:
            print("THIS SHOULDN HAPPEN AHHH")
            return None
        if len(legal)==1:
            return legal[0]

        # okay, so there are multiple actions for us to choose between.
        
        # let's keep track of how many games we simulate forward
        games = 0 # counter for number of games simulated (e.g., number of times "run_sim" is called)
        
        # begin the tree! keep track of time so do not exceed computation time limit
        begin = datetime.datetime.utcnow()
        while (datetime.datetime.utcnow() - begin) < self.calculation_time and games<self.nsims:
            # simulate games and store results in rewards and plays dictionaries.
            self.run_simulation()
            games+=1

        if self.verbose:
            # # display number of calls of 'run_simulation' and the time elapsed
            print('Num sims run:',games, '  Time elapsed:', datetime.datetime.utcnow() - begin)
            # self.print_tree()
        
        #DEBUGX
        # makes [(state, action1),...,(state, action_n)] for n legal actions
        statecopy = copy.deepcopy(state)
        # All possible action, next_state pairs
        moves_states = [(a.id, self.hash_and_store(statecopy.take_action(a,inplace=False))) for a in legal] #TODO: replace tuple with hash? (use hash table if need to un-hash state)


        # pick the move with the highest average reward
        percent_wins, move = max(((self.rewards.get((player, S), 0) / 
                                self.plays.get((player, S), 1), a)
                                for a, S in moves_states), 
                                key = lambda x: x[0])

        if self.verbose:
            # display the stats for each possible play
            for x in sorted(
                ((100 * self.rewards.get((player, S), 0) /
                self.plays.get((player, S), 1),
                self.rewards.get((player, S), 0),
                self.plays.get((player, S), 0), a)
                for a, S in moves_states),
                key = lambda y: y[0],
                reverse=True
            ):
                print("{3}: {0:.2f}% ({1} / {2})".format(*x))
            
            # print the max depth tree search
            print("Maximum depth searched:", self.max_depth)
        
        # return the move chosen
        # move is currently the unique id of the action, so find the legal action with this id
        action = next((a for a in legal if a.id == move), None) # I mean, i dont really want "none" to be an option at all! 
        return action
        
        
#     # this don't do anything yet
#     def print_tree(self):
#         board = self.game.tamagotchi_game
#         pass
    
    # play out a "random" game from the current position, then update stats with result
    def run_simulation(self):
        plays, rewards = self.plays, self.rewards
        
        visited_qs = set()
        states_copy = copy.deepcopy(self.states[:])
        simstate = states_copy[-1]
        player = simstate.players[simstate.turn]["name"] #self.identity #self.game.current_player_color(state)
        
        expand = True # you only expand once #YOEO
        for t in range(self.max_moves):
            legal = simstate.legal_actions() #self.game.legal_actions(states_copy) # get valid actions
 
            moves_states = [(a.id, self.hash_and_store(simstate.take_action(a,inplace=False))) for a in legal]

            if all(plays.get((player, S)) for a, S in iter(moves_states)):
                # if we have statistics on all legal moves, use them.
                # upper confidence bound (UCB) algorithm
#                 print("UCB choice")
                log_total = log(
                    sum(plays[(player, S)] for a, S in moves_states)
                )
                # list of value, action, shash tuples
                competitors = [((rewards[(player, S)] / plays[(player, S)]) +
                    self.C * sqrt(log_total / plays[(player, S)]), a, S)
                    for a, S in moves_states]
                highestval = max(competitors, key=lambda x: x[0])[0]
                # there could be equivalent actions (multiple maxima) so let us choose between those
                finalists = [x for x in competitors if x[0]==highestval]
                value, action, shash = random.choice(finalists)
                
                # print('took best choice')
                # self.n_best += 1
            
                # print(plays) 
                # # value of best
                # value, action, shash = max(
                #     (((rewards[(player, S)] / plays[(player, S)]) +
                #     self.C * sqrt(log_total / plays[(player, S)]), a, S)
                #     for a, S in moves_states),
                #     key = lambda x: x[0]
                # )
            else:
                # if we don't have stats on all legal moves, randomly pick one
#                 print("Random choice") (TODO: smarter default choice algo)
                # print('dont have stats on legal moves, doing random')  
                # self.n_random += 1
                action, shash = random.choice(moves_states)
                # print(plays)
            

            
                # # NEW let's have default policy be colorblind nearestneighbor
                # myplayer = simstate.players[simstate.turn]
                # sorted_legal = sorted(legal, key=lambda x: getManhattanDistance(myplayer,x))
                # # after sorting, first object is always pillow
                # chosen_legal = sorted_legal[1] # pick nearest object that is not the self lol 
                # action, shash = (chosen_legal['id'], self.hash_and_store(simstate.take_action(chosen_legal,inplace=False)))
                    

            # NEXT STATE from selected action
            simstate = self.get_state(shash)
            states_copy.append(simstate) # record

            # if we are in the expand phase and this is a new state-action pair
            if expand and (player, self.hash_and_store(simstate)) not in plays: 
                expand = False # you only expand once so this is it
                plays[(player, self.hash_and_store(simstate))] = 0 # initialize
                rewards[(player, self.hash_and_store(simstate))] = 0
                if t > self.max_depth:
                    self.max_depth = t
                    
            visited_qs.add((player, self.hash_and_store(simstate))) # add this state as visited
            
            # update the player
            player = simstate.players[simstate.turn]["name"]
            red_rwd, red_done = simstate.reward("red")
            purple_rwd, purple_done = simstate.reward("purple")
            done = red_done and purple_done
            
            if done: 
                # print("finished a game")
                # print("red reward ",red_rwd)
                # print("purple reward ",purple_rwd)
                break
        
        # print(visited_states, reward)
        for player, q in visited_qs: # for each visited state
            if (player, q) not in plays: # if we don't have stats on this state yet
                continue
            self.plays[(player, q)]+=1 # increase plays

            # the reward you consider depends on your reward policy - selfish, altruistic, or collaborative
            # are you trying to maximize your own rwd, your partner's reward, or both?
            if self.policy=="selfish": # IMPORTANT right now this assumes both players have selfish policy 
                if player=="red":
                    self.rewards[(player, q)]+=red_rwd # add up the reward you got
                else:
                    self.rewards[(player, q)]+=purple_rwd
            elif self.policy=="altruistic":
                if player=="red":
                    self.rewards[(player, q)]+=purple_rwd # add up the reward you got
                else:
                    self.rewards[(player, q)]+=red_rwd
            elif self.policy=="collaborative":
                self.rewards[(player, q)]+= red_rwd + purple_rwd # add up the reward you got

            # everyone gets punished for slowness regardless of reward policy
            # punish these bots for taking too long thoooooo
            penalty_factor = 0.0  # Scale factor
            self.rewards[(player, q)] -= penalty_factor * simstate.trial
            # self.rewards[(player,q)]-= simstate.trial # TEMPORAL COST - THIS PENALTY MAY NEED TO BE TUNED
            

    # here, we use string representation of hash rather than int that hash() itself gives
    def hash_and_store(self, s):
        # h = hash(s)
        h = str(hash(s))
        self.farmstatehash[h] = s
        return h

    def get_state(self, h):
        return self.farmstatehash[h]
