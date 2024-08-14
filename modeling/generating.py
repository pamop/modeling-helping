import bisect
import random
import farmgame
from model import Model


def generate_grid(steps: int, n_params: int, random_seed: int = None) -> list[list[float]]:
	if random_seed:
		random.seed = random_seed
	values = []
	for _ in range(n_params):
		unit_values = [(step + 1) / (steps + 1) for step in range(steps)]
		random.shuffle(unit_values)
		values.append(unit_values)
	# x parameters will give a list of x lists with n_params elements
	# We return a list with n_param lists of x elements
	return list(map(list, zip(*values)))


def draw_index(probabilities: list[float]) -> int:
	cumulative_probs = []
	cumulative_sum = 0
	for p in probabilities:
		cumulative_sum += p
		cumulative_probs.append(cumulative_sum)
	assert abs(cumulative_sum - 1.0) < 1e-8, "Probabilities must sum to 1"
	return bisect.bisect_left(cumulative_probs, random.random())



def choose_action(state: farmgame.Farm, model: Model) -> farmgame.Action:
	actions = state.legal_actions()
	index = draw_index(model.get_probs(state, actions))
	return actions[index]


def generate_game(start_state: farmgame.Farm, red_model: Model, purple_model: Model, turn_limit: int = None) -> farmgame.Game:
	game: farmgame.Game = []
	state = start_state
	while not state.is_done():
		current_colour = state.players[state.turn]['name']
		current_model = red_model if current_colour == 'red' else purple_model
		action = choose_action(state, current_model)
		game.append(farmgame.Transition(state, action))
		state = state.take_action(action, inplace=False)
		if turn_limit and state.trial >= turn_limit:
			return game
	game.append(farmgame.Transition(state, None))
	return game


def generate_session(red_model: Model, purple_model: Model, cost="low", resource="even", visibility="full", turn_limit=100) -> farmgame.Session:
	session: farmgame.Session = []
	for i in range(12):
		start_state = farmgame.configure_game(layer=f"Items{i:02d}", resourceCond=resource, costCond=cost, visibilityCond=visibility, redFirst=True)
		session.append(generate_game(start_state, red_model, purple_model, turn_limit))
	return session
