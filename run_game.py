from player import Player
from game_state import GameState, PlayerTurn
import time

def run_game(player1 : Player, player2 : Player, debug=False) -> PlayerTurn:
    """
    Runs a game between two players
    """
    # create a connect4 game
    game = GameState()

    # loop until the game is drawn
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
            time.sleep(1)

        possible = game.make_move(move)

        if not possible:
            # the move was invalid, the other player wins
            game.switch_turn()
            return game.player_turn

    return game.get_winner()

"""

# create an MCTS and AlphaBeta player
#player1 = alpha_beta.AlphaBeta(depth = 8)
player2 = alpha_beta.AlphaBeta(depth = 8)

# UNCOMMENT THIS TO TEST YOUR PLAYER
player1 = mcts.MCTS(iterations = 1000)

result = run_game(player1, player2)
if result == 0:
    print("player1 wins")
else:
    print("player2 wins")"""
