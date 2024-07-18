import bisect
import math
import random
from abc import ABC, abstractmethod
from typing import List

import farmgame


def draw_index(probabilities: List[float]) -> int:
	cumulative_probs = []
	cumulative_sum = 0
	for p in probabilities:
		cumulative_sum += p
		cumulative_probs.append(cumulative_sum)
	assert abs(cumulative_sum - 1.0) < 1e-8, "Probabilities must sum to 1"
	return bisect.bisect_left(cumulative_probs, random.random())


class Model(ABC):
	@abstractmethod
	def get_probs(self, state: farmgame.Farm, actions) -> List[float]:
		pass

	def choose_action(self, state: farmgame.Farm) -> farmgame.Action:
		actions = state.legal_actions()
		index = draw_index(self.get_probs(state, actions))
		return actions[index]


def compute_nll(game: farmgame.Game, red_model: Model, purple_model: Model) -> float:
	nll = 0
	for transition in game:
		current_colour = transition.state.players[transition.state.turn]['name']
		current_model = red_model if current_colour == 'red' else purple_model
		actions = transition.state.legal_actions()
		probs = current_model.get_probs(transition.state, actions)
		chosen_index = actions.index(transition.action)
		nll -= math.log(probs[chosen_index])
	return nll
