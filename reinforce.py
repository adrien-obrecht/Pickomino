
from alpha_beta_player import *
import numpy as np
from game_state import *

class FeatureMap:

    #an action is 1,...6 or 'S'
    def phi(self,state : GameState, action) -> np.array(float):
        pass

class Reinforce:
    #uses the REINFORCE algorithm (policy gradient) against a fixed alpha-beta adversary

    def __init__(self,w0,alpha,beta,fm:FeatureMap,gamma):
        self.w =  w0
        self.N = len(w0)
        self.adv = AlphaBetaPlayer(alpha,beta)
        self.phi = fm.phi
        self.gamma = gamma

    def pi(self,state:GameState):
        #returns the probability distribution other possible actions
        actions = state.possible_actions()
        sum = 0
        p = np.zeros(len(actions))
        for i in range(len(actions)):
            a = actions[i]
            p[i] = np.exp(np.sum(self.w*self.phi(state,a)))
            sum += p[i]
        p /= sum
        return (actions,p)

    def grad_log_pi(self,state:GameState,action):
        res = self.phi(state,action)
        actions, proba = self.pi(state)
        for i in range(len(actions)):
            res = res - proba[i]*self.phi(state,action)
        return res

    
    def train(self, num_games, alpha):
        #need to define rewards in a way
        #simulate the traj and then backtrackl
        for h in range(num_games):

            game = GameState()
            rewards = []
            gradJ = np.zeros(self.N)
            list_grad = []
            winner = None

            while not game.is_finished():
                if game.player_turn == PlayerTurn.PLAYER_1:
                    move = self.adv.act(game)
                else:
                    #the learning player plays
                    actions,proba = self.pi(game)
                    a = random.choices(actions,proba)

                    list_grad.append(self.grad_log_pi(game,a))

                    if a=='S':
                        #we need a score
                        player_index = int(game.player_turn.value) - 1 # Current player
                        opponent_index = int(not player_index) # Opponent player
                        #ATTENTION AUX INDEX
                        score = game.dice_state.score #
                        status = game.grid[score].status
                        opponent_stack = game.player_tiles[opponent_index]

                        tile = max(MAX_TILE,score)-MIN_TILE

                        #repetition in the code
                        if status == Tile.FACE_DOWN or (status== Tile.OWNED and (len(opponent_stack) == 0 or opponent_stack[-1].index != move.tile)):
                            #find the actual tile that the player chooses
                            found = False
                            for i in range(tile,-1,-1):
                                if game.grid[i].status==Tile.FACE_UP:
                                    move = Move(MoveType.STOP, tile=i)
                                    found = True
                                    break
                            if not found:
                                move = Move(MoveType.LOSE)
                        else:
                            move = Move(MoveType.STOP,tile=tile)
                    else:
                        move = Move(MoveType.CONTINUE,dice=a)
                
                possible = game.make_move(move)

                if not possible:
                    # the move was invalid, the other player wins
                    game.switch_turn()
                    winner = game.player_turn
                    break
            
            if not(winner):
                winner = game.get_winner()
            
            if winner == PlayerTurn.PLAYER_1:
                #adversary won
                R = -1
            else:
                R = 1

            T = len(list_grad)
            G = R

            for t in range(T-1,-1,-1):
                gradJ = gradJ + G*list_grad[t]

                R *= self.gamma

                G += R
                G *= self.gamma


            w = w + alpha*gradJ
        return

