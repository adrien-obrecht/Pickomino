from typing import List, Tuple
import numpy as np
import math

from alpha_beta_player import AlphaBetaPlayer
from run_game import *
from game_state import PlayerTurn

def create_bandit_pairs(grid_size: int) -> List[Tuple[float, float]]:
    """
    Creates all pairs of (alpha,beta) for a grid of side grid_size
    """
    pairs = []

    for a in np.linspace(0.0, 2.0, grid_size):
        for b in np.linspace(0.0, 2.0, grid_size):
            pairs.append((a, b))

    return pairs

import matplotlib.pyplot as plt
from IPython.display import clear_output
import time

def simulate_games_ucb(p : Player, grid_size : int, num_games: int, debug : bool = False) -> Tuple[Tuple[float, float], float]:
    """
    UCB algorithm
    """
    bandit_pairs = create_bandit_pairs(grid_size)
    num_pairs = len(bandit_pairs)
    wins = np.zeros(num_pairs, dtype=np.float64)
    counts = np.zeros(num_pairs, dtype=np.float64)

    for t in range(1,num_games+1):
        # Select the pair with the highest upper confidence bound
        ucb_values = []
        for i in range(num_pairs):
            if counts[i]==0:
                ucb_values.append(1000)
            else:
                prob = wins[i] / counts[i]
                coeff = math.sqrt(2 * math.log(t) / counts[i])
                if t < grid_size * grid_size * 0: # We first evaluate 0 times each cell
                    ucb_values.append(coeff)
                else:
                    ucb_values.append(prob + coeff)

        best_idx = np.argmax(ucb_values)
        best_pair = bandit_pairs[best_idx]
        
        adversary = AlphaBetaPlayer(*best_pair)

        winner = run_game(adversary, p)

        counts[best_idx] += 1


        if winner == PlayerTurn.PLAYER_1:
            wins[best_idx] += 1
            if debug:
                print(f"[{t}]Pair {best_pair} won. Winrate: of {wins[best_idx] / counts[best_idx]:.02f} ({wins[best_idx]} / {counts[best_idx]})")
        else:
            if debug:
                print(f"[{t}]Pair {best_pair} lost. Winrate: of {wins[best_idx] / counts[best_idx]:.02f} ({wins[best_idx]} / {counts[best_idx]})")
            
        if t % 1 == 0:
            # Clear the output to make room for the next plot
            clear_output(wait=True)
            # Update the plot
            grid = np.divide(wins, counts, out=np.zeros_like(wins, dtype=np.float64), where=counts!=0)
            plt.imshow(grid.reshape((grid_size, grid_size)), interpolation="bicubic", extent=[0, 2, 0, 2])
            plt.colorbar()
            plt.show()
            time.sleep(0.1)



    # Return the pair with the highest winrate
    probs = []
    for i in range(num_pairs):
        probs.append(wins[i] / counts[i])

    best_pair = bandit_pairs[np.argmax(probs)]

    if debug:
        #print all winrates
        print("Probabilities:")
        for i in range(num_pairs):
            print(bandit_pairs[i], probs[i])
    
        print(f"The best pair is {best_pair}, that wins with probability {max(probs)}")

    return (best_pair, max(probs))




