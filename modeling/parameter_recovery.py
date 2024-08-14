import random
import time
from scipy.optimize import minimize
from tqdm import *

from model import *
from simple_models import *
from generating import *

# Choose models for the players
player = Myopic()
n_params = len(player.describe_parameters())
n_points = 1000

# POWELL / L-BFGS-B / NELDER-MEAD / TNC / COBYLA / SLSQP
method = "SLSQP"

unit_params = generate_grid(n_points, n_params)
real_params = []
recovered_params = []

# Since we're using the same model for both players we'll iterate the
# parameter list 2 items at a time
start_time = time.process_time()
for unit1, unit2 in tqdm(list(zip(unit_params[::2], unit_params[1::2]))):
	# generate session
	real1 = player.unit_to_range(unit1)
	real2 = player.unit_to_range(unit2)
	real_params.extend([real1, real2])
	session = generate_session(
		player.create_from_list(real1),
		player.create_from_list(real2),
		cost = "low",
		resource = "even",
		visibility = "full"
	)

	# recover parameters
	x0 = player.unit_to_range([random.random() for _ in range(n_params)])
	x0.extend(player.unit_to_range([random.random() for _ in range(n_params)]))
	bounds = [(p.lower_bound, p.upper_bound) for p in player.describe_parameters()]
	bounds.extend([(p.lower_bound, p.upper_bound) for p in player.describe_parameters()])
	recovered = minimize(
		configure_and_compute_nll,
		args=(session, player, player),
		x0=x0,
		bounds=bounds,
		tol=0.0001,
		method=method
	)
	recovered_params.append(recovered.x[:n_params]) # add recovered red
	recovered_params.append(recovered.x[n_params:]) # add recovered purple
end_time = time.process_time()

filename = f"../parameter recovery/{type(player).__name__}_recovery_{method.lower()}.csv"
print(f"writing {filename}")
with open(filename, "w") as file:
	file.write(",".join([p.name for p in player.describe_parameters()]))
	file.write(",")
	file.write(",".join([f"{p.name}_recovered_{method.lower()}" for p in player.describe_parameters()]))
	file.write("\n")
	for i in range(n_points):
		file.write(",".join(str(p) for p in real_params[i]))
		file.write(",")
		file.write(", ".join(str(p) for p in recovered_params[i]))
		file.write("\n")
print(f"done, took {end_time - start_time} seconds")
