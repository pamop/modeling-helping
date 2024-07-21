import csv
import farmgame

def print_game(game: farmgame.Game) -> None:
	for transition in game:
		print([str(action) for action in transition.state.legal_actions()])
		player = transition.state.players[transition.state.turn]['name']
		if transition.action:
			print(f"{player} picks {transition.action}")

def is_true(string: str) -> bool:
	return string.lower().strip() == "true"

def create_state(row: dict) -> farmgame.Farm:
	farm = farmgame.configure_game(
		layer = row["objectLayer"],
		resourceCond = row["resourceCond"],
		costCond = row["costCond"],
		visibilityCond= row["visibilityCond"],
		redFirst = is_true(row["redFirst"]))
	# TODO: modify the state with the other columns in the row
	return farm

def get_id(row: dict, name: str) -> str:
	name = name.lower()
	for id in row["legalMoves"].split():
		if name in id.lower():
			return id
	return None

def create_action(row: dict) -> farmgame.Action:
	if is_true(row["gameover"]):
		return None
	if row["targetCat"] == "box":
		return farmgame.Farm.create_farmbox(farmgame.Farm.extract_location(get_id(row, "box")))
	elif row["targetCat"] == "none" or row["targetCat"] == "pillow":
		return farmgame.Farm.create_pillow(row["targetCat"], row["agent"], farmgame.Farm.extract_location(get_id(row, "none")))
	if row["targetCat"] == "timeout":
		return farmgame.Action("timeout", farmgame.ActionType.timeout, row["agent"], farmgame.Farm.extract_location(get_id(row, "none")), "timeout")
	elif "Veg" in row["targetCat"]:
		id = get_id(row, row["target"])
		return farmgame.Farm.create_veggie(row["target"][:-2].lower(), row["targetColor"], farmgame.Farm.extract_location(id), id)
	raise Exception(f"Please add logic to create an action for {row["targetCat"]}:\n{row}")

def load_sessions(filename: str, max_amount=-1) -> dict[str, farmgame.Session]:
	sessions = {}
	with open(filename) as in_file:
		for row in csv.DictReader(in_file):
			session_name = row["session"]
			session = sessions.get(session_name, [])
			# if we didn't already know about this session then it is a new one and we add it
			if not session:
				if max_amount >= 0 and len(sessions) + 1 == max_amount:
					# stop reading if we've seen enough
					break
				print(f"Reading session {len(sessions)} {session_name}", end="\r")
				sessions[session_name] = session
			# retrieve a game in this session or start a new one
			if int(row["turnCount"]) == 0:
				game = []
				session.append(game)
			else:
				game = session[int(row["gameNum"])]
			game.append(farmgame.Transition(create_state(row), create_action(row)))
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
