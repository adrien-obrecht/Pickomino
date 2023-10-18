import math
import itertools

def compute_prob(t):
    #compute the probability of rolling the dices in t
    n = len(t)
    res = math.factorial(n)
    for i in range(1,7):
        res /= math.factorial(t.count(i))
    return int(res)/6**n



class MDP():
    def __init__(self,c,r):
        """
        Initialization
        """
        self.c = c #value when lost
        self.r = r #reward vector
        self.value = {} #value of each state
        self.opti = {} #optimal move at each state, None if terminal state

    def explore(self,dices,used,score):
        """
        Dynamic programming starting with state (dices,tuple(sorted(used)),score)
        """
        state = dices,tuple(sorted(used)),score

        #memoization
        if state in self.value:
            return self.value[state]

        nb_dices = len(dices)
        rolled = set(dices)
        choices = rolled.difference(used)

        #check for terminal state

        if nb_dices==0:
            #we gathered all the dices
            self.opti[state] = None
            if (score<21):
                #the score is too low
                self.value[state] = self.c
                return self.c
            elif 6 not in used:
                #did not get a worm
                self.value[state] = self.c
                return self.c
            else:
                self.value[state] = self.r[score-21]
                return self.r[score-21]

        if not(choices):
            #we lost because all dices are already used
            self.value[state] = self.c
            self.opti[state] = None
            return self.c


        max_value = -100000000000#don't put zero because the maximum value can be negative
        max_idx = None

        for f in choices:
            #choose face f
            count = dices.count(f)
            new_used = used.copy()
            new_used.add(f)
            if (f<6):
                new_score = score + count*f
            else:
                new_score = score + 5*count

            s = 0
            it = itertools.combinations_with_replacement([1, 2, 3, 4, 5, 6], nb_dices-count)
            for new_dices in it:
                new_value = self.explore(new_dices, new_used, new_score)
                prob = compute_prob(new_dices)
                s += new_value * prob

            if s > max_value:
                max_value = s
                max_idx = f

        if (score<21):
            #the score is too low
            stop_value = self.c
        elif 6 not in used:
            stop_value = self.c
        else:
            stop_value = self.r[score-21]

        if stop_value > max_value:
            self.value[state] = stop_value
            self.opti[state] = "STOP"
        else:
            self.value[state] = max_value
            self.opti[state] = max_idx
        return self.value[state]



    def explore_all(self):
        """
        Dynamic programming starting from all possibles rolls of 8 dices
        """
        it = itertools.combinations_with_replacement([1,2,3,4,5,6], 8)
        for dices in it:
            # print(dices)
            self.explore(dices, set(), 0)

    def compute_value_total(self):
        """
        Computes the value of the game, needs to be called after explore_all
        """
        it = itertools.combinations_with_replacement([1,2,3,4,5,6], 8)
        p_total = 0
        for dices in it:
            prob = compute_prob(dices)
            p_total += prob * self.value[(dices, (), 0)]
        # print(p_total)
        return p_total
