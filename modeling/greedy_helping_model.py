from typing import List
import numpy as np
from scipy.special import softmax

import farmgame
from model import Model, Parameter

class GreedyHelpingModel(Model):
	def __init__(self, inverse_temperature = 1.0, helping_cost_ratio = 1.0, reciprocity = 0.0):
		"""
		Parameters:
		inverse_temperature (float):
			how deterministic this agent plays. A value of 0 will result in completely
			random play. A value of infinity will result in fully deterministic play.
			The temperature will scale the raw costs/rewards.
		helping_cost_ratio (float):
			how much more expensive is it to do a helping move. E.g. with a value of 2
			the agent will prefer picking their own veggies because the cost of walking
			to the neighbour's one is doubled. With a ratio of 1 the agent will not
			prefer one veggie colour over another. If the ratio is lower than 1 the
			agent will prefer picking the other colour's veggies.
		reciprocity (float):
			how likely the agent is to help after the neighbour has helped. The cost of actions
			that help the neighbour are divided by 1 + reciprocity if the neighbour has helped you
			before. So at reciprocity = 1 helping actions are half the cost, though they are
			still modulated by helping_cost_ratio too. At reciprocity = 0 there will be no
			change in preceived cost for helping actions.
		"""
		self.inv_temp = inverse_temperature
		self.helping_cost_ratio = helping_cost_ratio
		self.reciprocity = reciprocity
	
	def describe_parameters(self) -> list[Parameter]:
		return [
			Parameter("inverse_temperature", 0),
			Parameter("helping_cost_ratio", 0.001),
			Parameter("reciprocity", 0)
		]
	
	def create_from_list(self, params: list[float]) -> Model:
		return GreedyHelpingModel(params[0], params[1], params[2])


	def unit_to_range(self, unit: List[float]) -> List[float]:
		return [
			100 ** unit[0] - 1,
			(unit[1] + 0.5) ** 6,
			50 ** unit[2] - 1
		]

	def get_probs(self, state: farmgame.Farm, actions: List[farmgame.Action]):
		perceived_costs = []
		pass_index = -1
		farm_dropoff_index = -1
		can_harvest_own = False
		can_help = False
		own_color = state.whose_turn()["color"]
		for action in actions:
			if action.type == "pillow":
				# store fixed cost now, but keep the index so we can modify it later
				pass_index = len(perceived_costs)
				perceived_costs.append(state.get_cost(action))
			elif action.type == "box":
				# store the move cost now, but keep the index so we can modify it later
				farm_dropoff_index = len(perceived_costs)
				perceived_costs.append(state.get_cost(action))
			elif action.color == own_color:
				# getting your own veggies is simply taking the cost of getting there
				can_harvest_own = True
				perceived_costs.append(state.get_cost(action))
			else:
				# the perceived cost for harvesting the opponent's veggies takes
				# preferences for helping and reciprocating into account
				can_help = True
				cost_ratio = self.helping_cost_ratio
				if state.opponent_has_helped(own_color):
					cost_ratio /= 1 + self.reciprocity
				perceived_costs.append(cost_ratio * state.get_cost(action))
		if can_harvest_own:
			# Never pass or return to the farm if we can harvest our own
			if pass_index >= 0:
				perceived_costs[pass_index] = np.inf
			if farm_dropoff_index >= 0:
				perceived_costs[farm_dropoff_index] = np.inf
		elif not can_help and farm_dropoff_index >= 0:
			# if we can't pick anything up, but we can return to the farm, we should not pass
			if pass_index >= 0:
				perceived_costs[pass_index] = np.inf
		return softmax([-cost * self.inv_temp for cost in perceived_costs])
