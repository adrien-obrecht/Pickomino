import math
import itertools
from typing import Dict
import numpy as np

from dice_state import *
from move import *
from constants import *

mem = {}
def compute_prob(t):
    # compute the probability of rolling the dices in t
    if t in mem:
        return mem[t]
    n = len(t)
    res = math.factorial(n)
    for i in range(1,7):
        res /= math.factorial(t.count(i))
    mem[t] = int(res)/6**n
    return mem[t]



class MDP():
    opti : Dict[DiceState, Move]
    def __init__(self,c,r):
        """
        Initialization
        """
        assert c<=0, "c should be negative"
        self.c = c #value when lost
        self.r = r #reward vector
        self.value = {} #value of each state
        self.opti = {} #optimal move at each state, None if terminal state
        self.mem2 = {} #memorisation of value for a given number of dices

    def evaluate(self, state : DiceState):
        """
        Gives the reward for a given score
        """
        if state.getScore() < MIN_TILE:
            #the score is too low
            return self.c
        elif 6 not in state.getUsedDices():
            #did not get a worm
            return self.c
        else:
            #print(max(state.getScore(),36)-21,self.r)
            return self.r[min(state.getScore(),MAX_TILE)-MIN_TILE]#supposes that we used the max on r

    def explore(self, state : DiceState):
        """
        Dynamic programming starting with state
        """
        # memoization
        if state in self.value:
            return self.value[state]

        nb_dices = state.countDices()
        # rolled = state.getDices()
        # choices = rolled.difference(state.getUsedDices())
        choices = state.getChoices()

        # check for terminal state
        if nb_dices==0:
            # we gathered all the dices, we might have won
            if state.score>=MIN_TILE and 6 in state.used:
                self.opti[state] = Move(MoveType.STOP,tile=min(MAX_TILE,state.score)-MIN_TILE)
            else:
                self.opti[state] = Move(MoveType.LOSE)
            self.value[state] = self.evaluate(state)
            return self.value[state]

        if not(choices):
            # we lost because all dices are already used
            self.opti[state] = Move(MoveType.LOSE)
            self.value[state] = self.c
            return self.value[state]


        max_value = -(1<<30) # don't put zero because the maximum value can be negative
        max_idx = None

        for f in choices:
            # choose face f
            count = state.getDiceCount(f)
            new_used = state.getUsedDices().copy()
            new_used.add(f)
            if f < 6:
                new_score = state.getScore() + f * count
            else:
                new_score = state.getScore() + 5 * count

            s = 0

            state2 = (new_score, tuple(new_used), nb_dices-count)
            if state2 in self.mem2:#memoization before rolling the dices
                s = self.mem2[state2]
            
            else:
                """dices = list(new_used)
                for i in range(6):
                    if i+1 not in dices:
                        dices.append(i+1)"""
                it = itertools.combinations_with_replacement([1,2,3,4,5,6], nb_dices-count)
                for new_dices in it:
                    prob = compute_prob(new_dices)

                    #reduce the number of states by making the dices rolled "more similar" when they are equivalent
                    #m = min(new_used)
                    #new_dices = tuple(m if value in new_used else value for value in new_dices)

                    new_state = DiceState(new_dices, new_score, new_used)

                    new_value = self.explore(new_state)
                    
                    s += new_value * prob

                self.mem2[state2] = s

            if s > max_value:
                max_value = s
                max_idx = f
                
        stop_value = self.evaluate(state)

        if stop_value > max_value:
            self.value[state] = stop_value
            if state.score<21:#floating point error
                #print(stop_value,max_value,state)
                self.value[state] = max_value
                self.opti[state] = Move(MoveType.CONTINUE, dice=max_idx)
            else:
                #we return the truncated value of the score, then the player will find the best tile corresponding to this stop_value
                #because the player has the game state and we don't
                best_tile = min(state.getScore(),MAX_TILE)-MIN_TILE

                self.opti[state] = Move(MoveType.STOP, tile=best_tile)
        else:
            self.value[state] = max_value
            self.opti[state] = Move(MoveType.CONTINUE, dice=max_idx)
        return self.value[state]



    def explore_all(self):
        """
        Dynamic programming starting from all possibles rolls of NUM_DICES dices
        """
        it = itertools.combinations_with_replacement([1,2,3,4,5,6], NUM_DICES)
        k = 0
        for dices in it:
            if dices[0]>k:
                print(k)
                k+=1
            state = DiceState(dices, 0, set())
            self.explore(state)

    def compute_value_total(self):
        """
        Computes the value of the game, needs to be called after explore_all
        """
        it = itertools.combinations_with_replacement([1,2,3,4,5,6], NUM_DICES)
        p_total = 0
        k=0
        for dices in it:
            if dices[0]>k:
                print(k)
                k+=1
            prob = compute_prob(dices)
            state = DiceState(dices, 0, set())
            p_total += prob * self.value[state]
        # print(p_total)
        return p_total
