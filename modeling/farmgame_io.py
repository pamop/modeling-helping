import csv
import farmgame

def print_game(game: farmgame.Game) -> None:
	for transition in game:
		print([str(action) for action in transition.state.legal_actions()])
		print(transition)

def is_true(string: str) -> bool:
	return string.lower().strip() == "true"

def get_player_config(row: dict, name: str) -> dict:
	return {
		"loc": {
			"x": int(row[f"{name}Xloc"]),
			"y": int(row[f"{name}Yloc"])
		},
		"name": name,
		"capacity": int(row[f"{name}BackpackSize"]),
		"contents": [farmgame.Farm.create_item(id) for id in row[f"{name}Backpack"].split()],
		"score": int(row[f"{name}Score"]),
		"energy": int(row[f"{name}Energy"]),
		"bonuspoints": int(row[f"{name}Points"])
	}

def create_state(row: dict) -> farmgame.Farm:
	state = farmgame.Farm({
		"condition": {
			"resourceCond": row["resourceCond"],
			"costCond": row["costCond"],
			"visibilityCond": row["visibilityCond"]
		},
		"redplayer": get_player_config(row, "red"),
		"purpleplayer": get_player_config(row, "purple"),
		"redfirst": is_true(row["redFirst"]),
		"items": row["objectLayer"],
		"farmbox": {"boxcontents": [farmgame.Farm.create_item(id) for id in row[f"farmBox"].split()],},
		"stepcost": 2 if row["costCond"] == "high" else 1,
		"pillowcost": 5,
		"turn": int(row["turnCount"]) % 2,
		"trial": int(row["turnCount"])
	})
	return state

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
		return farmgame.Farm.create_veggie(row["target"][:-2].lower(), row["targetColor"], get_id(row, row["target"]))
	raise Exception(f"Please add logic to create an action for {row['targetCat']}:\n{row}")

def ascending_trial_num(file):
	previous_row = None
	for current_row in csv.DictReader(file):
		if previous_row:
			if previous_row["session"] == current_row["session"] and \
					int(previous_row["trialNum"]) > int(current_row["trialNum"]):
				# The previous row comes later. Keep it and return the current row first.
				yield current_row
				# Swap the row we're keeping
				current_row = previous_row
			else:
				# Normal order. Return the previous row first
				yield previous_row
		# Keep the row that we didn't return for the next comparison
		previous_row = current_row
	# Return the very last line that we held on to
	if previous_row:
		yield previous_row

def load_sessions(filename: str, max_amount=-1, print_progress=True) -> dict[str, farmgame.Session]:
	sessions = {}
	with open(filename) as in_file:
		for row in ascending_trial_num(in_file):
			session_name = row["session"]
			session = sessions.get(session_name, [])
			# if we didn't already know about this session then it is a new one and we add it
			if not session:
				if max_amount >= 0 and len(sessions) == max_amount:
					# stop reading if we've seen enough
					break
				if print_progress:
					print(f"Reading session {len(sessions) + 1} {session_name}", end="\r")
				sessions[session_name] = session
			# retrieve a game in this session or start a new one
			if int(row["turnCount"]) == 0:
				game = []
				session.append(game)
			else:
				game = session[int(row["gameNum"])]
			transition = farmgame.Transition(create_state(row), create_action(row))
			if len(game) > 0:
				transition.state.redplayer["has_helped"] = game[-1].state.redplayer["has_helped"] or game[-1].is_helping("red")
				transition.state.purpleplayer["has_helped"] = game[-1].state.purpleplayer["has_helped"] or game[-1].is_helping("purple")
			game.append(transition)
	if print_progress:
		print()
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
		current_player = state.whose_turn()
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
			action.id if action else "box", # target
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
			str(state.reward("purple")), # purple points
			str(state.reward("purple") + cumulative_purple),
			str(state.redplayer["backpack"]["capacity"]),
			str(state.redplayer["energy"]),
			str(state.redplayer["score"]),
			str(state.reward("red")), # red points
			str(state.reward("red") + cumulative_red),
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
