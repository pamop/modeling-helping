import csv
import farmgame

def print_game(game: farmgame.Game) -> None:
	for transition in game:
		print([str(action) for action in transition.state.legal_actions()])
		player = transition.state.players[transition.state.turn]['name']
		print(f"{player} picks {transition.action}")

def create_state(row: dict):
	farm = farmgame.configure_game(layer="Items00",resourceCond="even",costCond="low",visibilityCond="full",redFirst=True)
	return farm

def load_sessions(filename: str):
	sessions = {}
	with open(filename) as in_file:
		for row in csv.DictReader(in_file):
			games = sessions.get(row["session"], [])
			if not games:
				sessions[row["sessions"]] = games
			if row["turnCount"] == 0:
				game = []
				games.append[game]
			else:
				game = games[row["gameNum"]]
			game.append(create_state(row))

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

def write_game(file, game: farmgame.Game) -> None:	
	for transition in game:
		file.write(",".join([
			"", # subjid
			"", # session
			"", # trialnum
			"", # gameNum
			transition.state.costCond,
			transition.state.resourceCond,
			transition.state.visibilityCond,
			transition.state.redfirst,
			"", # counterbalance
			transition.state.objectLayer,
			"", # eventName
			transition.state.trial, # turnCount
			transition.state.players[transition.state.turn]["name"],
			"", # target
			"", # turnStartTimestamp
			"", # responseTime
			"", # decisionMadeTimestamp
			"", # dataSavedTimestamp
			transition.state.redplayer["loc"]["x"],
			transition.state.redplayer["loc"]["y"],
			transition.state.purpleplayer["loc"]["x"],
			transition.state.purpleplayer["loc"]["y"],
			" ".join(transition.state.farmbox["contents"]),
			" ".join(transition.state.purpleplayer["backpack"]["contents"]),
			" ".join(transition.state.redplayer["backpack"]["contents"]),
			"", # gameover
			" ".join(transition.state.legal_actions()),
			transition.state.purpleplayer["backpack"]["capacity"],
			transition.state.purpleplayer["energy"],
			transition.state.purpleplayer["score"],
			transition.state.purpleplayer["bonuspoints"],
			"", # cumulative points
			transition.state.redplayer["backpack"]["capacity"],
			transition.state.redplayer["energy"],
			transition.state.redplayer["score"],
			transition.state.redplayer["bonuspoints"],
			"", # cumulative points
			"", # lastTrial
			"", # energyExpense
			"", # taregtColor
			"", # targetCat
			"", # actionCat
		]))
		file.write("\n")
