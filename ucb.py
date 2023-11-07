from typing import List, Tuple
import numpy as np
import math

from alpha_beta_player import AlphaBetaPlayer
from run_game import *
from game_state import PlayerTurn

def create_bandit_pairs(grid_size: int) -> List[Tuple[float, float]]:
    """
    Creates all pairs of (alpha,beta)
    """
    pairs = []

    for a in np.linspace(0.0, 2.0, grid_size):
        for b in np.linspace(0.0, 2.0, grid_size):
            pairs.append((a, b))

    return pairs

"""def f(t : float):
    return 1 + t * math.log(t)**2"""

def simulate_games_ucb(p : Player, grid_size : int, num_games: int) -> Tuple[float, float]:
    """
    UCB algorithm
    """
    bandit_pairs = create_bandit_pairs(grid_size)
    num_pairs = len(bandit_pairs)
    wins = [0] * num_pairs
    counts = [0] * num_pairs
    
    for t in range(1,num_games+1):
        # Select the pair with the highest upper confidence bound
        print("[{}]".format(t),end="")
        ucb_values = []
        for i in range(num_pairs):
            if counts[i]==0:
                ucb_values.append(1000)
            else:
                prob = wins[i] / counts[i]
                coeff = math.sqrt(2 * math.log(t) / counts[i])
                ucb_values.append(prob + coeff)

        best_idx = np.argmax(ucb_values)
        best_pair = bandit_pairs[best_idx]
        
        adversary = AlphaBetaPlayer(*best_pair)

        winner = run_game(adversary, p)

        counts[best_idx] += 1
        if winner == PlayerTurn.PLAYER_1:
            wins[best_idx] += 1
            print(f"Pair {best_pair} won. Winrate: of {wins[best_idx] / counts[best_idx]:.02f} ({wins[best_idx]} / {counts[best_idx]})")
        else:
            print(f"Pair {best_pair} lost. Winrate: of {wins[best_idx] / counts[best_idx]:.02f} ({wins[best_idx]} / {counts[best_idx]})")


    # Return the pair with the highest winrate
    probs = []
    for i in range(num_pairs):
        probs.append(wins[i] / counts[i])

    best_pair = bandit_pairs[np.argmax(probs)]

    print("Probabilities:")
    for i in range(num_pairs):
        print(bandit_pairs[i], probs[i])
    
    print(f"The best pair is {best_pair}, that wins with probability {max(probs)}")

    return best_pair



