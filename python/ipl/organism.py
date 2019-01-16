

import math

import ipl.nnplanner as nnplanner




class Organism:
  """Give it a Game, and watch it play!
  """

  def __init__(self):
    self.action_generator = None
    self.outcome_likelihood_estimator = None
    self.outcome_generator = None
    self.lookahead_cache = None
  
    self.sensors = None
    self.action = None

    self.action_outcome_lookahead = 10

    self.verbosity = 0



  def configure(self, config):
    self.lookahead_cache = nnplanner.LookaheadCache()

    n_actuators = config['n_actuators']
    ag_params = nnplanner.ActionGeneratorParams(
        n_actuators, 1, 3, 100, 3)
    self.action_generator = nnplanner.ActionGenerator(ag_params)

    n_sensors = config['n_sensors']
    cg_params = nnplanner.OutcomeGeneratorParams(n_sensors, 100, 3, .75)
    self.outcome_generator = nnplanner.OutcomeGenerator(cg_params)

    ole_params = nnplanner.OutcomeLikelihoodEstimatorParams(
        n_sensors, n_actuators)
    self.outcome_likelihood_estimator = nnplanner.OutcomeLikelihoodEstimator(ole_params)

    victory_field_idx = config['victory_field_idx']
    def fn_utility(s): return s[victory_field_idx]
    self.outcome_generator.sensors_utility_metric = fn_utility
    self.outcome_generator.outcome_likelihood_estimator = self.outcome_likelihood_estimator
    self.outcome_generator.action_generator = self.action_generator
    self.outcome_generator.lookahead_cache = self.lookahead_cache

    self.action_generator.outcome_generator = self.outcome_generator
    
    self.experience_repo = nnplanner.ExperienceRepo()

    self.reset_state()



  def reset_state(self):
    self.sensors = None
    self.action = None
    self.lookahead_cache.clear()



  def maintenance(self):
    max_memory_before_consolidation = 1000000
    self.outcome_likelihood_estimator.consolidate_experiences(
      self.experience_repo, 
      max_memory_before_consolidation, 
      verbosity=self.verbosity)



  def handle_sensor_input(self, sensors):
    if self.verbosity > 0:
      print('ORGANISM: Received sensor input: {}'.format(sensors))

    if self.sensors and self.action:
      # Learn from the last turn's experience. This not only involves learning that
      # the thing we observed happened, but it also involves learning all the things
      # we thought might happen that didn't.
      self.experience_repo.add(
        self.sensors,
        self.action.actuators,
        sensors,
        [o.sensors for o in self.action.outcomes]
      )

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
    # NOTE: If we want the organism to act on an action plan, then we should at least retain
    # the action tree from its last action decision. Fittingly enough, that can still theoretically
    # be found in self.action, which we haven't cleared yet.
    self.lookahead_cache.clear()

    actions = self.action_generator.generate(
      self.sensors, 
      recursion_depth=self.action_outcome_lookahead
    )

    if self.verbosity > 0:
      print('ORGANISM: Generated actions (len={})'.format(len(actions)))
      for ac in actions:
        print('\t', ac)
        for oc in ac.outcomes:
          print('\t\t', oc)

    self.action = self.action_generator.selected_action
    if force_action:
      self.action = nnplanner.Action()
      self.action.actuators = force_action
      self.action.evaluate(
        self.sensors,
        self.outcome_generator
      )
    else:
      raise NotImplementedError("We're not selecting random actions yet.")

    if self.verbosity > 0:
      print('ORGANISM: Committing to action: {}'.format(self.action))

    return self.action




