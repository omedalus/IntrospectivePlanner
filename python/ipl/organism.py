

import math

import ipl.nnplanner as nnplanner


class Organism:
  """
  Give it a Game, and watch it play!
  """

  def __init__(self):
    self.game = None

    self.action_generator = None
    self.outcome_likelihood_estimator = None
    self.outcome_generator = None
  
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
    cg_params = nnplanner.OutcomeGeneratorParams(nsensors, nsensors*2)
    self.outcome_generator = nnplanner.OutcomeGenerator(cg_params)

    ole_params = nnplanner.OutcomeLikelihoodEstimatorParams(nsensors, nactions)
    self.outcome_likelihood_estimator = nnplanner.OutcomeLikelihoodEstimator(ole_params)

    victory_field_idx = game.io_vector_labels()['sensors'].index('VICTORY')
    def fn_utility(s): return s[victory_field_idx]
    self.outcome_generator.sensors_utility_metric = fn_utility
    


    self.action_generator.outcome_generator = self.outcome_generator

  def handle_sensor_input(self, sensors):
    if self.verbosity > 0:
      print('ORGANISM: Received sensor input: {}', sensors)

    # Learn from the last turn's experience.
    # Reinforce the actual observed subsequent sensor result.

    if self.sensors and self.action:
      self.outcome_likelihood_estimator.learn(
        self.sensors,
        self.action,
        sensors,
        self.action.outcomes,
        verbosity=self.verbosity
      )
    
    self.sensors = sensors
    self.action = None


  def choose_action(self, force_action=None):
    """Generate potential actions based on predicted outcomes.
    Arguments:
      force_action {list}: A vector of actuator states that the organism will be forced to perform.
    """
    self.action_generator.generate()
    self.action = self.action_generator.selected_action
    if force_action:
      self.action = nnplanner.Action()
      self.action.actuators = force_action
      self.action.evaluate(
        self.outcome_generator
      )
    else:
      raise NotImplementedError("We're not selecting random actions yet.")

    if self.verbosity > 0:
      print('ORGANISM: Committing to action: {}', self.action)

    return self.action




