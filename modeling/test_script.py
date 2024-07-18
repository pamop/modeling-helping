from typing import List
from scipy.optimize import minimize

import farmgame
import fitting
from farmgame_io import print_game
from first_choice_model import FirstChoiceModel
from generating import generate_game


prefer_first = FirstChoiceModel(1000)
dislike_first = FirstChoiceModel(0.1)

initial_state = farmgame.configure_game()
game = generate_game(initial_state, prefer_first, dislike_first)
print_game(game)

def game_nll(params: List[float], game: farmgame.Game) -> float:
	red_model = FirstChoiceModel(params[0])
	purple_model = FirstChoiceModel(params[1])
	return fitting.compute_nll(game, red_model, purple_model)

bounds = [(0.00001, None), (0.00001, None)]
recovered = minimize(game_nll, x0=[1, 1], args=(game,), bounds = bounds, method='L-BFGS-B')
print([f"{x:.20f}" for x in recovered.x])
