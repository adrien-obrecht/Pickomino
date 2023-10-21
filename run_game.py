import pickomino

def run_game(player1, player2):
    """
    Runs a game between two players
    """
    # create a connect4 game
    game = pickomino.Game()

    # loop until the game is drawn
    while not(game.game_end()):
        game.show()

        # reverse these if you want MCTS to go first
        if game.turn%2 == 1:
            move = player1.act()
        else:
            move = player2.act()

        # update the internal state of both players
        player1.feed(move)
        player2.feed(move)

        # if the move wins the game, then the game is finished
        game.make_move(move)

    return game.get_winner()


# create an MCTS and AlphaBeta player
#player1 = alpha_beta.AlphaBeta(depth = 8)
player2 = alpha_beta.AlphaBeta(depth = 8)

# UNCOMMENT THIS TO TEST YOUR PLAYER
player1 = mcts.MCTS(iterations = 1000)

result = run_game(player1, player2)
if result == 0:
    print("player1 wins")
else:
    print("player2 wins")
