import farmgame
from scipy.special import softmax
from model import Model, Parameter


class FirstChoiceModel(Model):
	"""
	This is a toy model to test generation and fitting code.
	The model will prefer the first choice offered to it by a certain factor.
	"""
	def __init__(self, first_choice_weight = 1.0) -> None:
		self.first_choice_weight = first_choice_weight

	def describe_parameters(self) -> list[Parameter]:
		return [Parameter("first_choice_weight", 0)]
	
	def create_from_list(self, params: list[float]) -> Model:
		return FirstChoiceModel(params[0])

	def unit_to_range(self, unit: list[float]) -> list[float]:
		return [(unit[0] + 0.5) ** 6]
	
	def get_probs(self, state: farmgame.Farm, actions: list[farmgame.Action]) -> list[float]:
		if len(actions) <= 1:
			return [1]
		weights = [1] * len(actions)
		weights[0] = self.first_choice_weight
		total = sum(weights)
		return [w / total for w in weights]


class MyopicColorblind(Model):
	"""
	Prefers the cheapest available action regardless of color.
	"""
	def __init__(self, inverse_temperature = 1.0) -> None:
		self.inverse_temperature = inverse_temperature
	
	def describe_parameters(self) -> list[Parameter]:
		return [Parameter("inverse_temperature", 0)]
	
	def create_from_list(self, params: list[float]) -> Model:
		return MyopicColorblind(params[0])

	def unit_to_range(self, unit: list[float]) -> list[float]:
		return [100 ** unit[0] - 1]
	
	def get_probs(self, state: farmgame.Farm, actions: list[farmgame.Action]) -> list[float]:
		weights = [-self.inverse_temperature * state.get_cost(action) for action in actions]
		return softmax(weights)


class Myopic(Model):
	"""
	Prefers the cheapest available action but prefers to pick the agent's own veggies.
	"""
	def __init__(self, inverse_temperature = 1.0, color_preference = 1.0) -> None:
		self.inverse_temperature = inverse_temperature
		self.color_preference = color_preference

	def describe_parameters(self) -> list[Parameter]:
		return [Parameter("inverse_temperature", 0), Parameter("color_preference", 0.001)]

	def create_from_list(self, params: list[float]) -> Model:
		return Myopic(params[0], params[1])
	
	def unit_to_range(self, unit: list[float]) -> list[float]:
		return [100 ** unit[0] - 1, (unit[0] + 0.5) ** 6]

	def get_probs(self, state: farmgame.Farm, actions: list[farmgame.Action]) -> list[float]:
		own_color = state.whose_turn()["color"]
		weights = [
			self.inverse_temperature * state.get_cost(action) *
			(-1 if action.color == own_color else -self.color_preference)
			for action in actions
		]
		return softmax(weights)
