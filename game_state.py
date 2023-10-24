from enum import Enum
from  dice_state import *
from move import Move, MoveType

class Tile(Enum):
    FACE_UP = 1
    FACE_DOWN = 2
    OWNED = 3

    def __str__(self):
        if self == Tile.FACE_UP:
            return "U"
        if self == Tile.FACE_DOWN:
            return "D"
        if self == Tile.OWNED:
            return "O"

class PlayerTurn(Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2
    
class TileState:
    def __init__(self, index, worm_value=1):
        self.status = Tile.FACE_UP
        self.worm = worm_value
        self.index = index
    
    def __repr__(self):
        return f"{self.status} ({self.worm})"

class GameState:
    def __init__(self):
        self.grid : list[TileState] = [TileState(i, i//4 + 1) for i in range(16)]
        self.player_turn : PlayerTurn = PlayerTurn.PLAYER_1
        self.dice_state : DiceState = DiceState(generate_random_dices(8), 0, set())
        self.player_tiles : tuple[list[TileState], list[TileState]] = [[], []]
        
    def __repr__(self):
        r = ""
        r += f"{self.player_turn}'s turn:\n"
        r += f"Dice State: {self.dice_state}\n"
        r += "Grid State: \n"
        for i in range(16):
            r += f"{self.grid[i].status} "
        r += "\n"
        for i in range(16):
            r += f"{self.grid[i].worm} "
        r += f"\nPlayer 1 Tiles: {[t.index for t in self.player_tiles[0]]}"
        r += f"\nPlayer 2 Tiles: {[t.index for t in self.player_tiles[1]]}"
        return r
    
    def is_finished(self):
        for i in range(16):
            if self.grid[i].status == Tile.FACE_UP:
                return False
        return True

    
    def lose_tile(self):
        player_index = int(self.player_turn.value) - 1
        if len(self.player_tiles[player_index]) > 0: # Player has at least one tile
            tile_returned = self.player_tiles[player_index].pop()
            self.grid[tile_returned.index].status = Tile.FACE_UP
            # self.tile_available += 1
            for i in range(15, -1, -1):
                if self.grid[i].status == Tile.FACE_UP:
                    if i == tile_returned:
                        continue  # if we had the biggest one, then we turn the one after
                    self.grid[i].status = Tile.FACE_DOWN
                    return

    def switch_turn(self):
        # It's another turn, we reroll the dices
        if self.player_turn == PlayerTurn.PLAYER_1:
            self.player_turn = PlayerTurn.PLAYER_2  
        else:
            self.player_turn = PlayerTurn.PLAYER_1
        self.dice_state = DiceState(generate_random_dices(8), 0, set())


    # return False if the move is invalid
    def make_move(self, move : Move) -> bool:
        if move.move_type == MoveType.STOP:
            player_index = int(self.player_turn.value) - 1 # Current player
            opponent_index = int(not self.player_turn.value) # Opponent player

            if move.tile + 21 > self.dice_state.score:
                # TODO check if it has a worm aswell
                print(f"Can't choose tile {move.tile} with a score of {self.dice_state.score}")
                return False

            if self.grid[move.tile].status == Tile.OWNED:
                # we steal the tile from the opponent
                opponent_stack = self.player_tiles[opponent_index]
                if len(opponent_stack) == 0 or opponent_stack[-1].index != move.tile:
                    print(f"Tile {move.tile} can't be stolen")
                    return False
                tile = self.player_tiles[opponent_index].pop()
                self.player_tiles[player_index].append(tile)
        
            if self.grid[move.tile].status == Tile.FACE_UP:
                self.grid[move.tile].status = Tile.OWNED
                self.player_tiles[player_index].append(self.grid[move.tile])
            
            if self.grid[move.tile].status == Tile.FACE_DOWN:
                print(f"Can't choose tile {move.tile}, it is turned down")
                return False

            self.switch_turn()
            return True
        
        if move.move_type == MoveType.LOSE:
            self.lose_tile()
            self.switch_turn()
            return True
        
        if move.move_type == MoveType.CONTINUE:
            if move.dice in self.dice_state.used:
                print(f"Can't choose dice {move.dice}, it has already been used")
                return False
            if not move.dice in self.dice_state.dices:
                print(f"Can't choose dice {move.dice}, it hasn't been rolled")
                return False
            n = self.dice_state.dices.count(move.dice)
            self.dice_state.used.add(move.dice)
            dice_score = max(5, move.dice)
            self.dice_state.score += n * dice_score
            self.dice_state.dices = generate_random_dices(len(self.dice_state.dices) - n)
            return True

    def get_winner(self) -> PlayerTurn:
        # TODO draws?
        if not self.player_tiles[1]:
            return PlayerTurn.PLAYER_1
        if not self.player_tiles[0]:
            return PlayerTurn.PLAYER_2
        s1 = sum(t.worm for t in self.player_tiles[0])
        m1 = max(t.index for t in self.player_tiles[0])
        s2 = sum(t.worm for t in self.player_tiles[1])
        m2 = max(t.index for t in self.player_tiles[1])
        
        if (s1, m1) > (s2, m2):
            return PlayerTurn.PLAYER_1
        return PlayerTurn.PLAYER_2
