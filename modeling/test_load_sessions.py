import utils
import farmgame_io

same_sessions = 0
same_games = 0
same_states = 0
diff_sessions = 0
diff_games = 0
diff_states = 0
incomplete_games = 0
sessions = farmgame_io.load_sessions("../data/trialdf.csv")
for session_nr, session_name in enumerate(sessions):
	print(f"Checking {session_nr + 1}/{len(sessions)} {session_name}", end="\r")
	differences_this_session = False
	for game_nr, game in enumerate(sessions[session_name]):
		derived_state = game[0].state
		differences_this_game = False
		for loaded in game:
			differences = utils.get_farm_differences(loaded.state, derived_state)
			if differences:
				differences_this_game = True
				diff_states += 1
				location = f"Session {session_name}, Game {game_nr}, Turn {derived_state.trial}"
				if loaded.state.turn != derived_state.turn and loaded.state.trial == derived_state.trial + 1:
					print(f"{location} is missing!")
					incomplete_games += 1
					break
				else:
					print(f"Session {session_name}, Game {game_nr}, Turn {loaded.state.trial} not equal")
					for difference in differences:
						print(difference)
			else:
				same_states += 1
			if loaded.action:
				derived_state = derived_state.take_action(loaded.action)
		if differences_this_game:
			diff_games += 1
			differences_this_session = True
		else:
			same_games += 1
	if differences_this_session:
		diff_sessions += 1
	else:
		same_sessions += 1
print()
print(f"             Sessions  Games  States")
print(f"incomplete:            {incomplete_games:>5}")
print(f"different:   {diff_sessions:>8}  {diff_games - incomplete_games:>5}  {diff_states:>5}")
print(f"identical:   {same_sessions:>8}  {same_games:>5}  {same_states:>5}")
print("-" * 35)
print(f"total:       {same_sessions + diff_sessions:>8}  {same_games + diff_games:>5}  {same_states + diff_states:>5}")
