from typing import List
from farmgame import Farm
from fitting import Model


class FirstChoiceModel(Model):
	"""
	This is a toy model to test generation and fitting code.
	The model will prefer the first choice offered to it by a certain factor.
	"""
	def __init__(self, first_choice_weight) -> None:
		self.first_choice_weight = first_choice_weight
	
	def get_probs(self, state: Farm, actions) -> List[float]:
		weights = [1] * len(actions)
		weights[0] = self.first_choice_weight
		total = sum(weights)
		return [w / total for w in weights]
