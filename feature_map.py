from game_state import *
import numpy as np
from constants import *

"""Feature map for policy gradient"""

def phi(state:GameState,action:Move):

    #action a is chosen w.p. proportionnal to exp(wT.phi(s,a))
    #wT.phi(s,a) should be very positive if good to take the action, very negative else
    
    dices = state.dice_state
    tab = np.zeros(NUM_FEATURES)
    """
    0 : gain de l'action
    1 : à quel point c'est pressant de prendre un worm
    2 : à quel point on est loin d'avoir une tile
    3 : score si stop
    4 : à quel point il nous reste des dés
    5 : le numéro du dé
    6 : nombre de dés used
    7 : value du coup si on peut voler une tile
    8 : ce qu'on perd si on perd
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

    d = action.dice

    #on a beaucoup de poids sur STOP, peut être scale des choses
    if action.move_type==MoveType.STOP:#choisi le dés d et s'arrête au tour d'après
        #on a une tile et un dice parce qu'on s'arrête au tour d'après
        score_after = dices.score+min(5,d)*dices.getDiceCount(d)
        dice_count = dices.countDices() - dices.getDiceCount(d)
        #on est sur que on a déjà un worm ou d est un worm

        tab[0] = d*dices.getDiceCount(d) #gain du choix de d
        tab[1] = 0
        tab[2] = score_after-(MIN_TILE+min_tile_up) #à quel point on est loin d'avoir une tile
        tab[3] = score_after #on veut s'arrêter sur un bon score
        tab[4] = -dice_count #on ne veut pas s'arrêter quand on a beacoup de dés
        tab[5] = d #on veut pick un bon dé
        tab[6] = len(dices.getUsedDices())+1 #on veut s'arrêter quand on a beaucoup de dés utilisés
        tab[7] = (opponent_stack[-1].index+1) if len(opponent_stack)>0 and opponent_stack[-1].index==score_after-MIN_TILE else 0 #valeur de la tile qu'on peut voler
        if (min_tile_up+MIN_TILE>=score_after):#valeur de ce qu'on perd si on perd
            tab[8] = -(player_stack[-1].index+1) if len(player_stack)>0 else 0
        else:
            tab[8] = 1
        tab[9] = 0

    elif action.move_type==MoveType.CONTINUE:  #continue et choisi le dés d
        tab[0] = d*dices.getDiceCount(d) #gain du choix de d
        tab[1] = -dices.getDiceCount(d) #on ne veut pas consommer trop de dés
        tab[2] = 0
        tab[3] = 0
        tab[4] = dices.countDices() #on veut continuer si on a des dés
        tab[5] = d #on veut pick un bon dé
        tab[6] = -len(dices.getUsedDices()) #on ne veut pas continuer quand on a beaucoup de dés utilisés
        tab[7] = 0 #on ne peut pas voler de tile
        tab[8] = 0
        tab[9] = (player_stack[-1].index+1) if len(player_stack)>0 else 0 #moins pas de risque de perdre notre tile si on continue
        

    return tab

#Another version of the feature map

# tab[0] = d*dices.getDiceCount(d)#gain du choix de d
# tab[1] = score_after-(MIN_TILE+min_tile_up) #à quel point on est loin d'avoir une tile
# tab[2] = score_after #on veut s'arrêter sur un bon score
# tab[3] = -dice_count #on ne veut pas s'arrêter quand on a beacoup de dés
# tab[4] = d #on veut pick un bon dé
# tab[5] = len(dices.getUsedDices())+1 #on veut s'arrêter quand on a beaucoup de dés utilisés
# tab[6] = (opponent_stack[-1].index+1) if len(opponent_stack)>0 and opponent_stack[-1].index==score_after-MIN_TILE else 0 #valeur de la tile qu'on peut voler
# if (min_tile_up+MIN_TILE>=score_after):#valeur de ce qu'on perd si on perd
#     tab[7] = -(player_stack[-1].index+1) if len(player_stack)>0 else 0
# else:
#     tab[7] = 1
# tab[8] = d*dices.getDiceCount(d) #gain du choix de d
# tab[9] = -dices.getDiceCount(d) #on ne veut pas consommer trop de dés
# tab[10] = dices.countDices() #on veut continuer si on a des dés
# tab[11] = d #on veut pick un bon dé
# tab[12] = -len(dices.getUsedDices()) #on ne veut pas continuer quand on a beaucoup de dés utilisés
# tab[13] = (player_stack[-1].index+1) if len(player_stack)>0 else 0 #moins pas de risque de perdre notre tile si on continue