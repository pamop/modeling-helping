import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax

class Agent:
    def __init__(self, n_actions, alpha, temperature):
        self.Q = np.zeros(n_actions)
        self.alpha = alpha
        self.temperature = temperature

    def choose(self, n_actions):
        probs = softmax(self.Q[:n_actions] / self.temperature)
        return np.random.choice(n_actions, p=probs)

    def learn(self, action, reward):
        self.Q[action] += self.alpha * (reward - self.Q[action])

    def get_probs(self, n_actions):
        return softmax(self.Q[:n_actions] / self.temperature)

# Generate example data with two alternating agents
def generate_data(n_subjects=10, n_trials=100, n_actions_range=(2, 10), true_alphas=(0.3, 0.4), true_temps=(1.5, 2.0)):
    data = []
    for subject in range(n_subjects):
        agents = [Agent(max(n_actions_range), alpha, temp) for alpha, temp in zip(true_alphas, true_temps)]
        for trial in range(n_trials):
            agent_id = trial % 2  # Alternate between agents
            n_actions = np.random.randint(n_actions_range[0], n_actions_range[1] + 1)
            action = agents[agent_id].choose(n_actions)
            reward = np.random.normal(agents[agent_id].Q[action], 1)
            agents[agent_id].learn(action, reward)
            data.append((subject, trial, agent_id, n_actions, action, reward))
    return np.array(data)

# Negative log-likelihood function for two agents
def neg_log_likelihood(params, data):
    alpha0, temp0, alpha1, temp1 = params
    nll = 0
    for subject in np.unique(data[:, 0]):
        subject_data = data[data[:, 0] == subject]
        max_actions = int(np.max(subject_data[:, 3]))
        agents = [Agent(max_actions, alpha0, temp0), Agent(max_actions, alpha1, temp1)]
        for _, _, agent_id, n_actions, action, reward in subject_data:
            agent_id = int(agent_id)
            n_actions = int(n_actions)
            action = int(action)
            probs = agents[agent_id].get_probs(n_actions)
            nll -= np.log(probs[action])
            agents[agent_id].learn(action, reward)
    return nll

# Fit the model for two agents
def fit_model(data):
    initial_params = [0.5, 1.0, 0.5, 1.0]  # Initial guess for alpha0, temp0, alpha1, temp1
    bounds = [(0, 1), (0, None), (0, 1), (0, None)]  # Bounds for alphas and temperatures
    result = minimize(neg_log_likelihood, initial_params, args=(data,), bounds=bounds, method='L-BFGS-B')
    return result

# Generate example data
data = generate_data()

# Fit the model
result = fit_model(data)

# Print results
print("Optimized parameters:")
print(f"Agent 0 - Alpha: {result.x[0]:.4f}, Temperature: {result.x[1]:.4f}")
print(f"Agent 1 - Alpha: {result.x[2]:.4f}, Temperature: {result.x[3]:.4f}")
print(f"Negative log-likelihood: {result.fun:.4f}")