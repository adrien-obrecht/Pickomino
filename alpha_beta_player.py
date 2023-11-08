from game_state import GameState, Tile
from move import Move, MoveType
from mdp2 import MDP2
from player import Player
from constants import *

class AlphaBetaPlayer(Player):

    memRC = {}

    def __init__(self,alpha,beta):
        self.alpha : float = alpha
        self.beta : float = beta
        self.mem_strats = {}
        self.current_MDP : MDP2 = None
    
    def get_r(self,game : GameState):
        #computes r with APPLYING MAX
        player_index = int(game.player_turn.value) - 1 # Current player
        opponent_index = int(not player_index) # Opponent player

        c = 0
        if len(game.player_tiles[player_index])>0:
            c = self.alpha*game.player_tiles[player_index][-1].worm

        r = [0]*NUM_TILES
        maxi = -(1<<30)

        opponent_stack = game.player_tiles[opponent_index]

        for i in range(NUM_TILES):
            if game.grid[i].status == Tile.FACE_UP:
                r[i] = i//STEP_SIZE+1
                maxi = max(maxi,r[i])
            if game.grid[i].status == Tile.OWNED and len(opponent_stack)>0 and opponent_stack[-1].index == i:
                r[i] = 2*self.beta*opponent_stack[-1].worm
                #don't update the max because you need to get the exact tile number to stole it
            else:
                maxi = max(maxi,-c)
                r[i] = maxi
        #I guess the cost is -alpha*top_tile.worm
        return r,-c

    def act(self, game : GameState) -> Move:
        #needs to decide if STOP, CONTINUE or else LOSE
        dice_state = game.dice_state
        nb_dice = dice_state.countDices()

        player_index = int(game.player_turn.value) - 1 # Current player
        opponent_index = int(not player_index) # Opponent player
        #if we are at the first dices roll use the MDP
        if nb_dice==NUM_DICES:
            r,c = self.get_r(game)
            # MEMOIZATION OVER (r,c) ---> NOT USED
            # if (tuple(r),c) in AlphaBetaPlayer.memRC:
            #     #print("reuse")
            #     self.current_MDP = AlphaBetaPlayer.memRC[(tuple(r),c)]
            #     self.current_MDP.explore(dice_state)
            # else:
            #     self.current_MDP = MDP(c,r)
            #     self.current_MDP.explore(dice_state)
            #     AlphaBetaPlayer.memRC[(tuple(r),c)] = self.current_MDP
            #no mem for now
            self.current_MDP = MDP2(c,r)
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

        # If stopping is better, we choose the tile as we know the whole game
        if move.move_type == MoveType.STOP:
            # We don't have a worm
            if move.dice != 6 and 6 not in dice_state.used:
                return Move(MoveType.LOSE)

            dice = move.dice
            score = dice_state.getScore() + min(move.dice, 5) * dice_state.getDiceCount(move.dice)
            tile = min(score, MAX_TILE) - MIN_TILE
            opponent_stack = game.player_tiles[opponent_index]

            # We try to find a tile that fits
            for i in range(tile,-1,-1):
                status = game.grid[i].status
                if status == Tile.FACE_UP:
                    return Move(MoveType.STOP, tile=i, dice=dice)
                if i == tile and status == Tile.OWNED and len(opponent_stack) != 0 and opponent_stack[-1].index == i:
                    return Move(MoveType.STOP, tile=i, dice=dice)
            return Move(MoveType.LOSE)
        return move

            
