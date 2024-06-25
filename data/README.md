# Data for computational helping two-person study

## gamedata

column name: datatype (units), description 
- subjid: category, a unique and anonymous identifier for each participant. the subjid is a string concatenating the session name and the color farmer this participant played as.
- session: category, a unique identifier for each session. one session consists of two participants playing 12 games (rounds) together.
- trialNum: int, chronological order of events recorded for each game. often skips even numbers because most "objectEncountered" events are excluded from this dataset (see turnCount and eventName description below)
- gameNum: int, number of the game this pair is playing (e.g., whether it is the first, second, etc. game they have played together). chronological order of games within a session.
- costCond: category, in ['low','high']. cost of each step (measured in tiles) the player takes. In 'low' condition, walking costs 1 energy per step. In 'high' condition, walking costs 2 energy per step. 
- resourceCond: category, in ['even','uneven']. whether both players have the same backpack size or not. in 'even' condition, both players have a backpack with size 4 (meaning they can carry 4 items at once before they must deposit them at the farmbox). in the 'uneven' condition, one player is randomly assigned a larger backpack of size 5 and the other player has a smaller backpack of size 3. though backpack size varies within a session in the 'uneven' condition, it is completely between subject - that is, each participant is assigned a single backpack size that is the same throughout all twelve games they play.
- visibilityCond: category, in ['self','full']. how much information about the current game state is displayed to the player. 'self' indicates self-only visibility condition, where player sees their own score and energy but not their partner's. 'full' indicates full visibility condition where player sees all available score and energy info regarding both players.
- redFirst: boolean, true if red player went first in this game
- counterbalance: category, in range(0,16). sixteen possible random orders for the sequence of initial environments (objectLayer) to counter order effects. orders are available in src/expGame/scenes/cleanup/utils.js in function getGameOrder(counterbalance).
- objectLayer: category, twelve values 'Items00' to 'Items11'. The name of the initial environment that was encountered in this game. All participants play all twelve game environments in counterbalanced order. 
- eventName: category, in ['targetPicked','objectEncountered'] Type of event that triggered this row's data to save. objectEncountered event is only included on last turn of each game to mark the final scores and game end event. all other events denote the player's action selection (rather than when their avatar reaches its target destination). (raw data has object encountered events for every turn but this data is not used in any of our analyses).
- turnCount: int, starts at 2 for each game because we dropped "gameStartRed" and "gameStartPurple" events which have no relevant information. increments by 1 on each turn.
- agent: category, color of the current player (player who is acting on this turn).
- target: category, action the player selected on this turn (depicted as a string of action type and (x,y) location)
- turnStartTimestamp: int (milliseconds), Unix epoch time in milliseconds stamped when the player's current turn began.
- responseTime: int (milliseconds), Difference between decisionMadeTimestamp and turnStartTimestamp (time between turn start and pointer down event).
- decisionMadeTimestamp: int (milliseconds), Unix epoch time in milliseconds stamped when the player chose their action (pointer down event).
- dataSavedTimestamp: int (milliseconds), Unix epoch time in milliseconds stamped when this row of data was saved to the database.
- redXloc, redYloc: red player's current x and y locations from top left.
- purpleXloc, purpleYloc: purple player's current x and y locations from top left.
- farmItems: object, list of all items in this game and their current (x,y) (from top left) locations. e.g., 'Tomato04(9,13)' becomes 'Tomato04(22,2)' when moved to red backpack.
- farmBox: object, list of all items currently in the farm box.
- purpleBackpack: object, list of all items currently in the purple player's backpack.
- redBackpack: object, list of items currently in red player's backpack.
- gameover: boolean, true if this is the last event of the current game.
- legalMoves: object, list of legal moves that the player can take on this turn. moves are strings labeled by action type and location. e.g., 'Tomato04(9,13)' denotes the arbitrary tomato number 4 at location (9,13). 'red_none(2,15)' indicates no movement (choosing pillow, or running out of time to choose) and staying in same location (2,15). 'box(16,5)' indicates choosing the box which is located at (16,5).
- purpleBackpackSize: int, size (capacity) of purple player's backpack (number of veggies that can be carried simultaneously).
- purpleEnergy: int, remaining amount of energy for red player.
- purpleScore: int, number of purple veggies in the farm box.
- purplePoints: int, purple player's total points earned across all games played so far.
- purplePointsCumulative: int, purple player's total points earned across all games played so far.
- redBackpackSize: int, size (capacity) of red player's backpack (number of veggies that can be carried simultaneously).
- redEnergy: int, remaining amount of energy for red player.
- redScore: int, number of red veggies in the farm box.
- redPoints: int, bonus points earned at the end of a game (redEnergy * redScore when gameover).
- redPointsCumulative: int, red player's total points earned across all games played so far.
- lastTrial: boolean, true if this event is from the last trial of the current game.

# demographic_data
- subjid	
- country	
- normal_vision	
- hispanic	
- race	
- color_blind	
- gender	
- education_level	
- fluent_english	
- household_income	
- dob
