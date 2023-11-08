from game_state import GameState, Tile
from move import Move, MoveType
from constants import *

class Player:
    """
    Interface for a player
    """
    def __init__(self):
        pass

    def act(self, game: GameState) -> Move:
        pass

class GreedyPlayer(Player):
    """
    Example of a greedy player with a basic strategy to test rungame
    """
    def __init__(self):
        super().__init__()

    def act(self, game : GameState) -> Move:
        score =  game.dice_state.score
        best_tile = None
        for i in range(NUM_TILES):
            if score > i+MIN_TILE and game.grid[i].status == Tile.FACE_UP:
                best_tile = i
            
        if best_tile is not None and 6 in game.dice_state.used:
            return Move(MoveType.STOP, tile=best_tile)
        
        
        best_dice = None
        for i in range(7):
            if i in game.dice_state.dices and i not in game.dice_state.used:
                best_dice = i
        if best_dice is not None:
            return Move(MoveType.CONTINUE, dice=best_dice)
        return Move(MoveType.LOSE)
            
        
