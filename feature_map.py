from game_state import *
import numpy as np

def phi(state:GameState,action:Move):
    #RETURNS a vector in R^n that represents 

    #action a is chosen w.p. proportionnal to exp(wT.phi(s,a))
    #wT.phi(s,a) should be very positive if good to take the action, very negative else
    #phi(s,a) could be big actually (in size), no real need to think
    #code everything in a numerical way, and then think about a good w0, or just let it be learned
    """
    state contains
    -the grid
    -player turn (nécessairement nous)
    -dice state:
        -score
        -dice choices
    -player piles
    action est dans les dice choices ou STOP
    """
    dices = state.dice_state
    tab = np.zeros(10)
    """
    0 : gain de l'action (0 si stop)
    1 : à quel point c'est pressant de prendre un worm
    2 : à quel point on est loin d'avoir une tile
    3 : score si stop
    4 : à quel point il nous reste des dés
    5 : le numéro du dé
    6 : le nombre de dés
    7 : nombre de dés used
    8 : value du coup si on peut voler une tile
    9 : ce qu'on perd si on perd

    """
    #calcul de la plus petite tile prenable
    min_tile_up = None
    for i in range(NUM_TILES):
        if state.grid[i].status==Tile.FACE_UP:
            min_tile_up = i
            break
    
    player_index = int(state.player_turn.value) - 1 # Current player
    opponent_index = int(not player_index) # Opponent player 
    opponent_stack = state.player_tiles[opponent_index]
    player_stack = state.player_tiles[player_index]

    if action.move_type==MoveType.STOP:
        tab[0] = 0
        tab[1] = 0
        tab[2] = MIN_TILE+min_tile_up-dices.score
        tab[3] = dices.score
        tab[4] = -dices.countDices() #on ne veut pas s'arrêter quand on a beacoup de dés
        tab[5] = 0
        tab[6] = 0
        tab[7] = len(dices.getUsedDices()) #on veut s'arrêter quand on a beaucoup de dés utilisés
        tab[8] = (opponent_stack[-1].index+1) if len(opponent_stack)>0 and opponent_stack[-1].index==dices.score-MIN_TILE else 0
        if (min_tile_up+MIN_TILE>=dices.score):
            tab[9] = -(player_stack[-1].index+1) if len(player_stack)>0 else 0
        else:
            tab[9] = 1

    elif action.move_type==MoveType.CONTINUE:  #continue et choisi le dés d
        d = action.dice
        tab[0] = d*dices.getDiceCount(d)
        tab[1] = -dices.countDices() if d==6 else 0# si il y a beaucoup de dés il n'est pas urgent de prendre un worm
        tab[2] = 0
        tab[3] = 0
        tab[4] = dices.countDices() - dices.getDiceCount(d) #plus on a de dés mieux c'est
        tab[5] = d
        tab[6] = dices.getDiceCount(d)
        tab[7] = -len(dices.getUsedDices())
        tab[8] = 0
        tab[9] = 0

    return tab