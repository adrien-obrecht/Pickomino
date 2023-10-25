from typing import List, Tuple
import numpy as np
import math

from alpha_beta_player import AlphaBetaPlayer
from run_game import *
from game_state import PlayerTurn

def create_bandit_pairs(grid_size: int) -> List[Tuple[float, float]]:
    pairs = []

    for a in np.linspace(0.0, 2.0, grid_size):
        for b in np.linspace(0.0, 2.0, grid_size):
            pairs.append((a, b))

    return pairs

def f(t : float):
    return 1 + t * math.log(t)**2

def simulate_games_ucb(p : Player, grid_size : int, num_games: int) -> Tuple[float, float]:
    bandit_pairs = create_bandit_pairs(grid_size)
    num_pairs = len(bandit_pairs)
    wins = [0] * num_pairs
    counts = [0] * num_pairs
    
    for t in range(num_games):
        # Select the pair with the highest upper confidence bound
        ucb_values = []
        for i in range(num_pairs):
            prob = wins[i] / (counts[i] + 1)
            coeff = math.sqrt(2 * math.log(f(t+1)) / (counts[i] + 1))
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
    
    print(f"The best pair is {best_pair}, that wins with probability {max(probs)}")

    return best_pair



