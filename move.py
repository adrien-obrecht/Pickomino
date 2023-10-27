from enum import Enum
from constants import *

class MoveType(Enum):
    LOSE = 1
    STOP = 2
    CONTINUE = 3

class Move:
    def __init__(self, move_type: MoveType, tile=None, dice=None):
        assert isinstance(move_type, MoveType), "Invalid move type!"

        if move_type == MoveType.STOP:
            assert tile is not None and 0 <= tile <= NUM_TILES-1, "Invalid Tile! Range is 0 to 15."

        if move_type == MoveType.CONTINUE:
            assert dice is not None and 1 <= dice <= 6, "Invalid Dice! Range is 1 to 6."

        self.move_type = move_type
        self.tile = tile
        self.dice = dice

    def __str__(self):
        if self.move_type == MoveType.LOSE:
            return "Lose"
        elif self.move_type == MoveType.STOP:
            return f"Stop and pick tile {self.tile}"
        else: # continue
            return f"Continue with dice {self.dice}"
