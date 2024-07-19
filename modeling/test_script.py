from typing import List
from scipy.optimize import minimize

import farmgame
import fitting
from farmgame_io import print_game
from first_choice_model import FirstChoiceModel
from greedy_helping_model import GreedyHelpingModel
from generating import generate_session

# set up the two players
prefer_first = FirstChoiceModel(1000)
greedy = GreedyHelpingModel("purple", 100, 10, 5)
# generate the session
session = generate_session(prefer_first, greedy)
# print the first game of the session as illustration
print_game(session[0])

# Gather stats
red_help_count = 0
purple_help_count = 0
for game in session:
	if game[-1].state.redplayer["has_helped"]:
		red_help_count += 1
	if game[-1].state.purpleplayer["has_helped"]:
		purple_help_count += 1
print()
print(f"Red has helped in {red_help_count} games")
print(f"Purple has helped in {purple_help_count} games")
if red_help_count == 0:
	print("Purple's reciprocity can not be fitted")

def session_nll(params: List[float], session: farmgame.Session) -> float:
	red_model = FirstChoiceModel(params[0])
	purple_model = GreedyHelpingModel("purple", params[1], params[2], params[3])
	return sum([fitting.compute_nll(game, red_model, purple_model) for game in session])

x0 = [1, 1, 1, 1]
bounds = [
	(0.00001, None), # first choice weight
	(0, None), # greedy inverse temperature
	(0, None), # greedy helping cost ratio
	(0, None)  # greedy reciprocity
]
print("\nRecovering parameters...")
recovered = minimize(session_nll, x0=x0, args=(session,), bounds = bounds, method='L-BFGS-B')
print(f"Red first choice weight: {recovered.x[0]}")
print(f"Purple inverse temperature: {recovered.x[1]}")
print(f"Purple helping cost ratio: {recovered.x[2]}")
print(f"Purple reciprocity: {recovered.x[3]}")
