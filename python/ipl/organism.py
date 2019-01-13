

import math
import sklearn.neural_network # pylint: disable=E0401

import ipl.nnplanner as nnplanner


class Organism:
  """
  Give it a Game, and watch it play!
  """

  def __init__(self):
    self.game = None

    self.action_generator = None
    self.consequence_likelihood_estimator = None
    self.consequence_generator = None
  
    self.sensors = None
    self.action = None

    self.verbosity = 0


  def init_game(self, game):
    self.game = game
    if self.verbosity > 0:
      print('Initializing organism to game: {}'.format(game.title))

    nactions = len(self.game.io_vector_labels()['actuators'])
    ag_params = nnplanner.ActionGeneratorParams(nactions, 1, 3, nactions*2)
    self.action_generator = nnplanner.ActionGenerator(ag_params)

    nsensors = len(self.game.io_vector_labels()['sensors'])
    cg_params = nnplanner.ConsequenceGeneratorParams(nsensors, nsensors*2)
    self.consequence_generator = nnplanner.ConsequenceGenerator(cg_params)

    ninputs = 2 * nsensors + nactions
    nhidden = 2 * ninputs + int(math.sqrt(ninputs)) + 1
    self.consequence_likelihood_estimator = sklearn.neural_network.MLPRegressor(
        hidden_layer_sizes=(nhidden),
        activation='logistic',
        solver='lbfgs',
        warm_start=True)

  def handle_sensor_input(self, sensors, force_action=None):
    if self.verbosity > 0:
      print('ORGANISM: Received sensor input: {}', sensors)

    # First, learn from the last turn's experience.
    # Reinforce the actual observed subsequent sensor result.

    if self.sensors and self.action:
      observed_training_vector = self.sensors + self.action + sensors
      self.consequence_likelihood_estimator.fit(
          [observed_training_vector], [1])

      # TODO: For each predicted outcome of the selected action,
      # calculate the magnitude of the counterfactuality, and
      # punish accordingly.
    
    # Generate potential actions based on predicted outcomes.
    self.sensors = sensors
    self.action_generator.generate()
    self.action = self.action_generator.selected_action
    if force_action:
      self.action = force_action

    if self.verbosity > 0:
      print('ORGANISM: Committing to action: {}', self.action)

    return self.action




