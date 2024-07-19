from typing import List
from scipy.optimize import minimize

import farmgame
import fitting
from farmgame_io import print_game
from first_choice_model import FirstChoiceModel
from generating import generate_session


prefer_first = FirstChoiceModel(1000)
dislike_first = FirstChoiceModel(0.1)

session = generate_session(prefer_first, dislike_first)
print_game(session[0])

def session_nll(params: List[float], session: farmgame.Session) -> float:
	red_model = FirstChoiceModel(params[0])
	purple_model = FirstChoiceModel(params[1])
	return sum([fitting.compute_nll(game, red_model, purple_model) for game in session])

bounds = [(0.00001, None), (0.00001, None)]
recovered = minimize(session_nll, x0=[1, 1], args=(session,), bounds = bounds, method='L-BFGS-B')
print([f"{x:.20f}" for x in recovered.x])
