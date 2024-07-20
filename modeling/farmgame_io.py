import csv
import farmgame

def print_game(game: farmgame.Game) -> None:
	for transition in game:
		print([str(action) for action in transition.state.legal_actions()])
		player = transition.state.players[transition.state.turn]['name']
		if transition.action:
			print(f"{player} picks {transition.action.type}")

def create_state(row: dict) -> farmgame.Farm:
	farm = farmgame.configure_game(
		layer = row["objectLayer"],
		resourceCond = row["resourceCond"],
		costCond = row["costCond"],
		visibilityCond= row["visibilityCond"],
		redFirst = row["redFirst"].strip() == "TRUE")
	# TODO: modify the state with the other columns in the row
	return farm

def create_action(row: dict) -> farmgame.Action:
	# TODO
	return None

def load_sessions(filename: str) -> dict[str, farmgame.Session]:
	sessions = {}
	with open(filename) as in_file:
		for row in csv.DictReader(in_file):
			session = sessions.get(row["session"], [])
			if not session:
				sessions[row["sessions"]] = session
			if row["turnCount"] == 0:
				game = []
				session.append[game]
			else:
				game = session[row["gameNum"]]
			game.append(farmgame.Transition(create_state(row), create_action(row))
	return sessions

def write_header(file) -> None:
	file.write(",".join([
		"subjid",
		"session",
		"trialNum",
		"gameNum",
		"costCond",
		"resourceCond",
		"visibilityCond",
		"redFirst",
		"counterbalance",
		"objectLayer",
		"eventName",
		"turnCount",
		"agent",
		"target",
		"turnStartTimestamp",
		"responseTime",
		"decisionMadeTimestamp",
		"dataSavedTimestamp",
		"redXloc",
		"redYloc",
		"purpleXloc",
		"purpleYloc",
		"farmItems",
		"farmBox",
		"purpleBackpack",
		"redBackpack",
		"gameover",
		"legalMoves",
		"purpleBackpackSize",
		"purpleEnergy",
		"purpleScore",
		"purplePoints",
		"purplePointsCumulative",
		"redBackpackSize",
		"redEnergy",
		"redScore",
		"redPoints",
		"redPointsCumulative",
		"lastTrial",
		"energy_expense",
		"targetColor",
		"targetCat",
		"actionCat"
	]))
	file.write("\n")

def write_game(file, game: farmgame.Game, session_name="", trial_nr=0, game_nr=0, cumulative_red=0, cumulative_purple=0) -> None:
	for transition in game:
		state = transition.state
		action = transition.action
		current_player = state.players[state.turn]
		game_over = not action
		file.write(",".join([
			session_name + current_player["color"],
			session_name,
			str(trial_nr + state.trial), # trialnum
			str(game_nr), # gameNum
			state.costCond,
			state.resourceCond,
			state.visibilityCond,
			"TRUE" if state.redfirst else "FALSE",
			"", # counterbalance
			state.objectLayer,
			"objectEncountered" if game_over else "targetPicked", # eventName
			str(state.trial - 1 if game_over else state.trial), # turnCount
			current_player["color"],
			action.id.split("(")[0] if action else "box", # target
			"", # turnStartTimestamp
			"", # responseTime
			"", # decisionMadeTimestamp
			"", # dataSavedTimestamp
			str(state.redplayer["loc"]["x"]),
			str(state.redplayer["loc"]["y"]),
			str(state.purpleplayer["loc"]["x"]),
			str(state.purpleplayer["loc"]["y"]),
			f'"{" ".join([str(item) for item in state.items])}"',
			f'"{" ".join([str(item) for item in state.farmbox.contents])}"',
			f'"{" ".join([str(item) for item in state.purpleplayer["backpack"]["contents"]])}"',
			f'"{" ".join([str(item) for item in state.redplayer["backpack"]["contents"]])}"',
			"TRUE" if game_over else "FALSE", # game over
			f'"{" ".join([str(action) for action in state.legal_actions()])}"',
			str(state.purpleplayer["backpack"]["capacity"]),
			str(state.purpleplayer["energy"]),
			str(state.purpleplayer["score"]),
			str(state.reward("purple")[0]), # purple points
			str(state.reward("purple")[0] + cumulative_purple),
			str(state.redplayer["backpack"]["capacity"]),
			str(state.redplayer["energy"]),
			str(state.redplayer["score"]),
			str(state.reward("red")[0]), # red points
			str(state.reward("red")[0] + cumulative_red),
			"TRUE" if game_over else "FALSE", # lastTrial
			str(state.get_cost(action)) if action else "",
			"box" if not action or action.type == farmgame.ActionType.box else action.color if action.type == farmgame.ActionType.veggie else "none",
			action.get_target() if action else "box",
			action.get_category(current_player["color"]) if action else "box"
		]))
		file.write("\n")

def create_file(filename: str, session: farmgame.Session, session_name, with_header=True) -> None:
	with open(filename, "w") as file:
		if with_header:
			write_header(file)
		trial_start = 0
		cumulative_red = 0
		cumulative_purple = 0
		for game_nr, game in enumerate(session):
			write_game(file, game, session_name, trial_start, game_nr, cumulative_red, cumulative_purple)
			trial_start += len(game)
			cumulative_red += game[-1].state.reward("red")
			cumulative_purple += game[-1].state.reward("purple")
