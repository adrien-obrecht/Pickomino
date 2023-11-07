from player import Player
from game_state import GameState, PlayerTurn
import time

def run_game(player1 : Player, player2 : Player, debug=False) -> PlayerTurn:
    """
    Runs a game between two players
    """
    # create a Pickomino game
    game = GameState()

    # loop until the game is over
    while not game.is_finished():
        if game.player_turn == PlayerTurn.PLAYER_1:
            move = player1.act(game)
        else:
            move = player2.act(game)

        if debug:
            print(game)
            print()
            
            print(move)
            print()

        possible = game.make_move(move)

        if not possible:
            # the move was invalid, the other player wins
            game.switch_turn()
            return game.player_turn
    if debug:
        print("End of the game")
    return game.get_winner()

