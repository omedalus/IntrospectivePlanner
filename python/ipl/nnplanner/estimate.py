
import math
import random

from .action import Action
from .outcome import Outcome


class OutcomeLikelihoodEstimatorParams:
  """Configuration for an estimator.
  """
  def __init__(self, n_sensors, n_actuators, **kwargs):
    self.n_sensors = n_sensors
    self.n_actuators = n_actuators

    self.forget_delta_threshold = kwargs.get('forget_delta_threshold') 
    if self.forget_delta_threshold is None:
      self.forget_delta_threshold = 0.005
    #self.n_registers = 0


class OutcomeLikelihoodEstimator:
  """An object that can be given a set of vectors representing both
  a current state and a subsequent state, and tries to estimate the
  likelihood of seeing that subsequent state given the current one."""

  def __init__(self, organism, params):
    """Create the estimator.
    Arguments:
      params {OutcomeLikelihoodEstimatorParams} -- Configuration info.
    """
    self.organism = organism
    self.params = params




  def __relative_similarity(self, s1, s2):
    """Compute the proximity of two sensor vectors.
    Arguments:
      s1 {Outcome|list} -- A sensor vector to compare against.
      s2 {Outcome|list} -- A sensor vector to compare against.
    Returns:
      {float} -- A float between 0 and 1, where 1 means the two vectors are identical 
          and 0 means the two vectors differ by at least .5 in every element. 
    """
    if isinstance(s1, Outcome):
      s1 = s1.sensors

    if isinstance(s2, Outcome):
      s2 = s2.sensors

    if len(s1) != len(s2):
      raise ValueError('Sensor vectors need to be the same length.')

    # This is just a const that tells us how different we permit two different
    # sensor values to be before we give no reward at all for the counterfactual
    # one. By setting it to <=.5, we can ensure that the trainee can't "cheat" by
    # always outputting exactly .5 and always getting partial credit regardless of
    # if the desired value is 0 or 1.
    max_piecewise_diff = .5

    # I could do something cleverly Pythonic here, but I'd really rather make
    # the math explicit and obvious to make coding and debugging easier.
    total_prox = 0
    for se1, se2 in zip(s1, s2):
      abs_diff = abs(se1 - se2)
      magnified_diff = abs_diff / max_piecewise_diff
      truncated_magnified_diff = min(magnified_diff, 1)
      prox = 1 - truncated_magnified_diff
      total_prox += prox

    normalized_prox = total_prox / len(s1)
    return normalized_prox



  def learn(self, experience_repo):
    """Tell the estimator that certain combinations of sensors, actions, etc.,
    led to certain observed outcome, and not any of the other outcomes that the estimator
    might have previously believed had high likelihoods.
    Arguments:
      experience_repo {ExperienceRepo} -- Repository of all experiences the organism has ever had.
    """
    pass



  def estimate(self, sensors_prev, action, sensors_next):
    """Compute the likelihood that, after performing action action in the context of sensor state
    sensors_prev, that the next sensor state encountered will be sensors_next.
    Returns:
      {float} -- The estimated relative likelihood of seeing the outcome.
    """
    if self.organism is None or self.organism.experience_repo is None:
      raise ValueError('Experience repo must be specified.')
    p, ci = self.organism.experience_repo.get_outcome_probability(sensors_prev, action, sensors_next)
    return p, ci


  def get_known_outcomes(self, sensors_prev, action, prob_threshold=0):
    if self.organism is None or self.organism.experience_repo is None:
      raise ValueError('Experience repo must be specified.')
    sensorsprobs = self.organism.experience_repo.lookup_outcomes(sensors_prev, action, prob_threshold=0)

    outcomes = []
    for sensorsprob in sensorsprobs:
      sensors = sensorsprob[0]
      prob = sensorsprob[1]
      ci = sensorsprob[2]
      c = Outcome()
      c.sensors = sensors
      c.probability = prob
      c.probability_95ci = ci
      outcomes.append(c)

    return outcomes


  def get_known_actions(self, sensors_prev):
    if self.organism is None or self.organism.experience_repo is None:
      raise ValueError('Experience repo must be specified.')
    actuatorses = self.organism.experience_repo.lookup_actions(sensors_prev)

    actions = []
    for actuators in actuatorses:
      a = Action()
      a.actuators = actuators
      actions.append(a)

    return actions


  def consolidate_experiences(self, max_experience_repo_size, verbosity=0):
    """Tries to determine which experiences can be removed from the repo, that will have a negligible effect
    on the estimate results.
    Arguments:
      max_experience_repo_size {int} -- The biggest we want to let the experience repo get. We'll
          stop consolidating if it's smaller than this.
    Returns:
      {list} -- A list of Experience objects that can be removed from the repo with no significant change
          to the output of the estimator.
    """
    raise NotImplementedError('Not implemented anymore.')
    if verbosity > 0:
      print('Repo size before consolidation: {}'.format(
        len(experience_repo)))

    pass

    if verbosity > 0:
      print('Repo size after consolidation: {}'.format(
          len(experience_repo)))






