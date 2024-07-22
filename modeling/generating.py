import farmgame
from fitting import Model


def generate_game(start_state: farmgame.Farm, red_model: Model, purple_model: Model) -> farmgame.Game:
	game: farmgame.Game = []
	state = start_state
	done = False
	while not done:
		current_colour = state.players[state.turn]['name']
		current_model = red_model if current_colour == 'red' else purple_model
		action = current_model.choose_action(state)
		game.append(farmgame.Transition(state, action))
		state = state.take_action(action, inplace=False)
		_, done = state.reward(current_colour)
	return game


def generate_session(red_model: Model, purple_model: Model, cost="low", resource="even", visibility="full") -> farmgame.Session:
	session: farmgame.Session = []
	for i in range(12):
		start_state = farmgame.configure_game(layer=f"Items{i:02d}", resourceCond=resource, costCond=cost, visibilityCond=visibility, redFirst=True)
		session.append(generate_game(start_state, red_model, purple_model))
	return session
