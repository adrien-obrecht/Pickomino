import math
import itertools
from typing import Dict
import numpy as np

from dice_state import *
from move import *
from constants import *

mem = {}
def compute_prob(t):
    # compute the probability of rolling the dices in the throw t
    if t in mem:
        return mem[t]
    n = len(t)
    res = math.factorial(n)
    for i in range(1,7):
        res /= math.factorial(t.count(i))
    mem[t] = int(res)/6**n
    return mem[t]



class MDP2():
    opti : Dict[DiceState, Move]
    def __init__(self,c,r):
        """
        Initialization
        """
        assert c<=0, "c should be negative"
        self.c = c #value when lost
        self.r = r #reward vector
        self.value = {} #value of each state
        #optimal move at each state, None if terminal state
        #a key is a State
        self.opti = {}
        #memorisation of value for a given number of dices, ie BEFORE rolling the dices
        #a key is a score, a number of dices, and used dices
        self.mem2 = {} 
        self.opti2 = {}

    def evaluate(self, state : DiceState):
        """
        Gives the reward for a given score, equiv before throwing the dice
        """
        if state.getScore() < MIN_TILE:
            #the score is too low
            return self.c
        elif 6 not in state.getUsedDices():
            #did not get a worm
            return self.c
        else:
            #get the value in the reward vector
            return self.r[min(state.getScore(),MAX_TILE)-MIN_TILE]
        
    def explore_before(self, state2):
        score, tuple_used, nb_dices = state2
        used = set(tuple_used)
        it = itertools.combinations_with_replacement([1,2,3,4,5,6], nb_dices)
        #iterate over all possible dice rolls
        s=0

        for new_dices in it:
            prob = compute_prob(new_dices)

            new_state = DiceState(new_dices, score, used)

            new_value = self.explore_after(new_state)
            
            s += new_value * prob
        
        continue_value = s
        state = DiceState((), score, used)
        stop_value = self.evaluate(state)

        if continue_value > stop_value:
            self.mem2[state2] = continue_value
            self.opti2[state2] = Move(MoveType.CONTINUE,dice=1)
        else:
            self.mem2[state2] = stop_value
            self.opti2[state2] = Move(MoveType.STOP,tile=max(min(state.getScore(),MAX_TILE)-MIN_TILE,0))
        return self.mem2[state2]


    def explore_after(self, state : DiceState):
        """
        Dynamic programming starting with a dice state
        """
        # memoization
        if state in self.value:
            return self.value[state]

        nb_dices = state.countDices()
        choices = state.getChoices()

        # check for terminal state
        if nb_dices==0:
            # we gathered all the dices, we might have won
            if state.score>=MIN_TILE and 6 in state.used:#we won because we have a worm and a high enough score
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
            #compute new score
            if f < 6:
                new_score = state.getScore() + f * count
            else:
                new_score = state.getScore() + 5 * count

            s = 0

            state2 = (new_score, tuple(new_used), nb_dices-count)
            if state2 in self.mem2:#memoization before rolling the dices
                s = self.mem2[state2]
            
            else:
                s = self.explore_before(state2)
                

            if s > max_value:
                max_value = s
                max_idx = f
        #max_value = value of the state
        #max_idx = face to choose
                
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
                #print(k)
                k+=1
            state = DiceState(dices, 0, set())
            self.explore_after(state)

    def compute_value_total(self):
        """
        Computes the value of the game, needs to be called after explore_all
        """
        it = itertools.combinations_with_replacement([1,2,3,4,5,6], NUM_DICES)
        p_total = 0
        k=0
        for dices in it:
            if dices[0]>k:
                #print(k)
                k+=1
            prob = compute_prob(dices)
            state = DiceState(dices, 0, set())
            p_total += prob * self.value[state]
        return p_total