
from alpha_beta_player import *
import numpy as np
from game_state import *
from run_game import *

class FeatureMap:

    def phi(self,state : GameState, action:Move) -> np.array(float):
        pass

class Reinforce(Player):
    #uses the REINFORCE algorithm (policy gradient) against a fixed alpha-beta adversary

    def __init__(self,w0,alpha,beta,fm,gamma):
        self.w =  w0
        self.N = len(w0)
        self.adv = AlphaBetaPlayer(alpha,beta)
        self.phi = fm
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

    def grad_log_pi(self,state:GameState,move:Move):
        res = self.phi(state,move)
        actions, proba = self.pi(state)
        for i in range(len(actions)):
            res = res - proba[i]*self.phi(state,actions[i])
        return res
    
    def act(self,game:GameState) -> Move:
        #the learning player plays
        actions,proba = self.pi(game)
        #print(proba)
        if len(proba)==0:
            return Move(MoveType.LOSE)
        
        a = random.choices(actions,weights=proba,k=1)[0]

        if a.move_type==MoveType.STOP:
            #we need a score
            player_index = int(game.player_turn.value) - 1 # Current player
            opponent_index = int(not player_index) # Opponent player
            #ATTENTION AUX INDEX
            score = game.dice_state.score + min(a.dice, 5) * game.dice_state.getDiceCount(a.dice) ####

            tile = min(MAX_TILE,score)-MIN_TILE

            status = game.grid[tile].status
            opponent_stack = game.player_tiles[opponent_index]

            

            #finding the actual tile we pick
            if status == Tile.FACE_DOWN or (status== Tile.OWNED and (len(opponent_stack) == 0 or opponent_stack[-1].index != a.tile)):
                #find the actual tile that the player chooses
                found = False
                for i in range(tile,-1,-1):
                    if game.grid[i].status==Tile.FACE_UP:
                        move = Move(MoveType.STOP, tile=i, dice=a.dice)
                        return move
                return Move(MoveType.LOSE)
            
            return Move(MoveType.STOP,tile=tile, dice=a.dice)
        
        return a
    
    def train(self, num_games, alpha):

        for h in range(num_games):
            if h%100==0:
                print("step:",h)
                print("w:",self.w)
            
            game = GameState()
            rewards = []
            gradJ = np.zeros(self.N)
            list_grad = []
            winner = None

            while not game.is_finished():
                if game.player_turn == PlayerTurn.PLAYER_1:
                    move = self.adv.act(game)
                else:
                    move = self.act(game)

                    list_grad.append(self.grad_log_pi(game,move))
                
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

            norm = np.linalg.norm(gradJ)
            
            if (h%100==0):
                print("gradient norm:",norm)

            gradJ = gradJ/norm

            self.w = self.w + alpha*gradJ
        return
    
    #evaluates the performance of the learning player over num_games games
    def evaluate(self, num_games, debug=False):
        nb_wins = 0

        for h in range(num_games):

            winner = run_game(self.adv,self,debug)

            if winner == PlayerTurn.PLAYER_2:
                nb_wins+=1
        return nb_wins/num_games



