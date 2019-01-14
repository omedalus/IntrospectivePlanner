

import math

import ipl.nnplanner as nnplanner




class Organism:
  """Give it a Game, and watch it play!
  """

  def __init__(self):
    self.action_generator = None
    self.outcome_likelihood_estimator = None
    self.outcome_generator = None
  
    self.sensors = None
    self.action = None

    self.verbosity = 0



  def configure(self, config):
    n_actuators = config['n_actuators']
    ag_params = nnplanner.ActionGeneratorParams(
        n_actuators, 1, 3, n_actuators*2)
    self.action_generator = nnplanner.ActionGenerator(ag_params)

    n_sensors = config['n_sensors']
    cg_params = nnplanner.OutcomeGeneratorParams(n_sensors, n_sensors*2)
    self.outcome_generator = nnplanner.OutcomeGenerator(cg_params)

    ole_params = nnplanner.OutcomeLikelihoodEstimatorParams(
        n_sensors, n_actuators)
    self.outcome_likelihood_estimator = nnplanner.OutcomeLikelihoodEstimator(ole_params)

    victory_field_idx = config['victory_field_idx']
    def fn_utility(s): return s[victory_field_idx]
    self.outcome_generator.sensors_utility_metric = fn_utility

    self.action_generator.outcome_generator = self.outcome_generator
    
    self.experience_repo = nnplanner.ExperienceRepo()

    self.reset_state()



  def reset_state(self):
    self.sensors = None
    self.action = None


  def handle_sensor_input(self, sensors):
    if self.verbosity > 0:
      print('ORGANISM: Received sensor input: {}'.format(sensors))

    if self.sensors and self.action:
      # Learn from the last turn's experience.
      # Reinforce the actual observed subsequent sensor result.
      experience = nnplanner.Experience(
        self.sensors,
        self.action.actuators,
        sensors,
        [o.sensors for o in self.action.outcomes]
      )

      self.experience_repo.experiences.add(experience)
      
      self.outcome_likelihood_estimator.learn(self.experience_repo)

      if self.verbosity > 0:
        print('ORGANISM: Experience repo size: {}'.format(len(self.experience_repo.experiences)))
    
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
      print('ORGANISM: Committing to action: {}'.format(self.action))

    return self.action




