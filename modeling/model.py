from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import NamedTuple

import farmgame


class Parameter(NamedTuple):
	name: str
	lower_bound: float | None = None
	upper_bound: float | None = None


class Model(ABC):
	@abstractmethod
	def describe_parameters(self) -> list[Parameter]:
		pass
	
	@abstractmethod
	def create_from_list(self, params: list[float]) -> Model:
		pass

	@abstractmethod
	def unit_to_range(unit: list[float]) -> list[float]:
		"""
		Transform a list of numbers between 0 and 1 to parameter values. Values around 0.5
		should be neutral if possible. Values of 0 and 1 should be at or near the limits.
		This method can be used for random initializations and grid searches.
		"""
		pass
	
	@abstractmethod
	def get_probs(self, state: farmgame.Farm, actions: list[farmgame.Action]) -> list[float]:
		pass


def compute_game_nll(game: farmgame.Game, red_model: Model, purple_model: Model) -> float:
	nll = 0
	for transition in game:
		current_colour = transition.state.players[transition.state.turn]['name']
		current_model = red_model if current_colour == 'red' else purple_model
		actions = transition.state.legal_actions()
		if actions and len(actions) > 1:
			probs = current_model.get_probs(transition.state, actions)
			chosen_index = actions.index(transition.action)
			if probs[chosen_index] <= 0:
				return float('inf')
			nll -= math.log(probs[chosen_index])
	return nll

def compute_session_nll(session: farmgame.Session, red_model: Model, purple_model: Model) -> float:
	return sum([compute_game_nll(game, red_model, purple_model) for game in session])

def configure_and_compute_nll(params: list[float], session: farmgame.Session, red_model: Model, purple_model: Model) -> float:
	n_red_p = len(red_model.describe_parameters())
	red_instance = red_model.create_from_list(params[:n_red_p])
	purple_instance = purple_model.create_from_list(params[n_red_p:])
	return compute_session_nll(session, red_instance, purple_instance)
