from game_state import GameState, Tile
from move import Move, MoveType
from mdp import MDP
from player import Player

class AlphaBetaPlayer(Player):

    memRC = {}

    def __init__(self,alpha,beta):
        self.alpha : float = alpha
        self.beta : float = beta
        self.mem_strats = {}
        self.current_MDP : MDP = None
    
    def get_r(self,game : GameState):
        #computes r with applying max
        player_index = int(game.player_turn.value) - 1 # Current player
        opponent_index = int(not player_index) # Opponent player

        c = 0
        if len(game.player_tiles[player_index])>0:
            c = self.alpha*game.player_tiles[player_index][-1].worm

        r = [0]*16
        maxi = -(1<<30)

        opponent_stack = game.player_tiles[opponent_index]

        for i in range(16):
            if game.grid[i].status == Tile.FACE_UP:
                r[i] = i//4+1
                maxi = max(maxi,r[i])
            if game.grid[i].status == Tile.OWNED and len(opponent_stack)>0 and opponent_stack[-1].index == i:
                r[i] = 2*self.beta*opponent_stack[-1].worm
                #don't update the max because you need to get the exact tile number to stole it
            else:
                maxi = max(maxi,-c)
                r[i] = maxi
        #I guess the cost is -alpha*top_tile.worm
        #print(r,c)
        return r,-c

    def act(self, game : GameState) -> Move:
        #needs to decide if STOP, CONTINUE or else LOSE
        dice_state = game.dice_state
        nb_dice = dice_state.countDices()

        player_index = int(game.player_turn.value) - 1 # Current player
        opponent_index = int(not player_index) # Opponent player
        #if we are at the first dices roll use the MDP
        if nb_dice==8:
            r,c = self.get_r(game)
            if (tuple(r),c) in AlphaBetaPlayer.memRC:
                print("reuse")
            else:
                AlphaBetaPlayer.memRC[(tuple(r),c)]=None
            #no mem for now
            self.current_MDP = MDP(c,r)
            self.current_MDP.explore(dice_state)
        # print("start dico")
        # for i in self.current_MDP.opti:
        #     print(i,self.current_MDP.opti[i])
        # print("fin dico")
        #else the MDP is already computed
        # if dice_state not in self.current_MDP.opti:
        #     print("key error")
        move = self.current_MDP.opti[dice_state]
        #print("according to dico")
        #print(dice_state,move)
        tile = move.tile

        #case in which you need to find a lower tile: face down or owned but not on top
        if move.move_type == MoveType.STOP:
            status = game.grid[tile].status
            opponent_stack = game.player_tiles[opponent_index]
            if status == Tile.FACE_DOWN or (status== Tile.OWNED and (len(opponent_stack) == 0 or opponent_stack[-1].index != move.tile)):
                #find the actual tile that the player chooses
                for i in range(tile,-1,-1):
                    if game.grid[i].status==Tile.FACE_UP:
                        return Move(MoveType.STOP, tile=i)
                return Move(MoveType.LOSE)

        return move

            
