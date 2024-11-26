import random
from scipy.optimize import minimize

import farmgame
import model
from simple_models import FirstChoiceModel
from greedy_helping_model import GreedyHelpingModel
from generating import generate_session

print("\nGenerating session...")
# Choose models for the players
red_model = FirstChoiceModel()
purple_model = FirstChoiceModel()
# Create a random set of parameters
n_red_p = len(red_model.describe_parameters())
n_pur_p = len(purple_model.describe_parameters())
actual = red_model.unit_to_range([random.random() for _ in range(n_red_p)])
actual.extend(purple_model.unit_to_range([random.random() for _ in range(n_pur_p)]))
red_model = red_model.create_from_list(actual[:n_red_p])
purple_model = purple_model.create_from_list(actual[n_red_p:])
# generate the session
session = generate_session(red_model, purple_model)


def session_nll(params: list[float], session: farmgame.Session, red_model: model.Model, purple_model: model.Model) -> float:
	n_red_p = len(red_model.describe_parameters())
	red_instance = red_model.create_from_list(params[:n_red_p])
	purple_instance = purple_model.create_from_list(params[n_red_p:])
	return sum([model.compute_session_nll(game, red_instance, purple_instance) for game in session])


# set up and run recovery
x0 = red_model.unit_to_range([0.5] * len(red_model.describe_parameters()))
x0.extend(purple_model.unit_to_range([0.5] * len(purple_model.describe_parameters())))
bounds = [(p.lower_bound, p.upper_bound) for p in red_model.describe_parameters()]
bounds.extend([(p.lower_bound, p.upper_bound) for p in purple_model.describe_parameters()])
print("\nRecovering parameters...")
recovered = minimize(session_nll, x0=x0, args=(session,red_model,purple_model), bounds=bounds, options={'disp': True})

# print results
p_names = [p.name for p in red_model.describe_parameters()]
p_names.extend([p.name for p in purple_model.describe_parameters()])
for i, name in enumerate(p_names):
	color = "Red" if i < len(red_model.describe_parameters()) else "Purple"
	print(f"{color} {name} {actual[i]} recovered {recovered.x[i]}")
