
import math
import sklearn.neural_network  # pylint: disable=E0401

from .action import Action
from .outcome import Outcome
from .experience import Experience


class OutcomeLikelihoodEstimatorParams:
  """Configuration for an estimator.
  """
  def __init__(self, n_sensors, n_actuators):
    self.n_sensors = n_sensors
    self.n_actuators = n_actuators
    #self.n_registers = 0


class OutcomeLikelihoodEstimator:
  """An object that can be given a set of vectors representing both
  a current state and a subsequent state, and tries to estimate the
  likelihood of seeing that subsequent state given the current one."""

  def __init__(self, params):
    """Create the estimator.
    Arguments:
      params {OutcomeLikelihoodEstimatorParams} -- Configuration info.
    """
    self.params = params

    ninputs = 2 * params.n_sensors + params.n_actuators
    nhidden = 2 * ninputs + int(math.sqrt(ninputs)) + 1

    # TODO: Play around with number and size of hidden layers.
    self.neuralnet = sklearn.neural_network.MLPRegressor(
        hidden_layer_sizes=(nhidden),
        activation='logistic',
        solver='lbfgs')



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
    tvecs = experience_repo.training_vectors()
    Xall = [tv[0] for tv in tvecs]
    yall = [tv[1] for tv in tvecs]

    self.neuralnet.fit(Xall, yall)



  def estimate(self, experience_possible):
    """Compute the likelihood that, after performing action action in the context of sensor state
    sensors_prev, that the next sensor state encountered will be sensors_next.
    Arguments:
      experience_possible {Experience} -- An experience that the organism might have.
    Returns:
      {float} -- The estimated relative likelihood of seeing the outcome.
    """
    query_vector = experience_possible.observed_vector()
    predictions = self.neuralnet.predict([query_vector])
    return predictions[0]








