

import math
import sklearn.neural_network # pylint: disable=E0401

from .nnplanner import ActionGenerator, ActionGeneratorParams

class Organism:
  """
  Give it a Game, and watch it play!
  """

  def __init__(self):
    self.game = None
    self.action_generator = None
    self.next_state_predictor = None
  
    self.sensors = None
    self.action = None

  def init_game(self, game):
    self.game = game

    nactions = len(self.game.io_vector_labels()['actuators'])
    params = ActionGeneratorParams(nactions, 1, 3, nactions*2)
    self.action_generator = ActionGenerator(params)

    nsensors = len(self.game.io_vector_labels()['sensors'])

    ninputs = 2 * nsensors + nactions
    nhidden = 2 * ninputs + int(math.sqrt(ninputs)) + 1
    self.next_state_predictor = sklearn.neural_network.MLPRegressor(
        hidden_layer_sizes=(nhidden),
        activation='logistic',
        solver='lbfgs',
        warm_start=True)

  def handle_sensor_input(self, sensors, force_action=None):
    # First, learn from the last turn's experience.
    # Reinforce the actual observed subsequent sensor result.

    if self.sensors and self.action:
      observed_training_vector = self.sensors + self.action + sensors
      self.next_state_predictor.fit([observed_training_vector], [1])

      # TODO: For each predicted outcome of the selected action,
      # calculate the magnitude of the counterfactuality, and
      # punish accordingly.
    
    # Generate potential actions based on predicted outcomes.
    self.sensors = sensors
    self.action_generator.generate()
    self.action = self.action_generator.selected_action
    if force_action:
      self.action = force_action
    return self.action




