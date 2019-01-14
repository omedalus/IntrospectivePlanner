
import math
import sklearn.neural_network  # pylint: disable=E0401

from .action import Action
from .outcome import Outcome


class OutcomeLikelihoodEstimatorParams:
  """Configuration for an estimator.
  """
  def __init__(self, n_sensors, n_actuators):
    self.n_sensors = n_sensors
    self.n_actuators = n_actuators
    #self.n_registers = 0

    self.__neuralnet = None


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
    self.__neuralnet = sklearn.neural_network.MLPRegressor(
        hidden_layer_sizes=(nhidden),
        activation='logistic',
        solver='lbfgs',
        warm_start=True)



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




  def learn(self, sensors_prev, action, sensors_observed, sensorses_expected, verbosity=0):
    """Tell the estimator that a certain combination of sensors, actions, etc.,
    let to an observed outcome, and not any of the other outcomes that the estimator
    might have previously believed had high likelihoods.
    Arguments:
      sensors_prev {Outcome|list} -- The previous sensor vector, in which context the action was taken.
      action {Action|list} -- The action that was taken in the context of the sensors_prev sensor state.
      sensors_observed {Outcome|list} -- The sensor state that was subsequently observed.
      sensorses_expected {list(Outcome)|list(list)} -- Other sensor states that weren't observed.
    """
    if isinstance(sensors_prev, Outcome):
      sensors_prev = sensors_prev.sensors

    if isinstance(action, Action):
      action = action.actuators

    if isinstance(sensors_observed, Outcome):
      sensors_observed = sensors_observed.sensors

    # Teach it what *did* happen.
    observed_training_vector = []
    observed_training_vector += sensors_prev
    observed_training_vector += action
    observed_training_vector += sensors_observed
    self.__neuralnet.fit([observed_training_vector], [1])

    if verbosity > 0:
      print('ESTIMATOR: Observed vector: {}  s=1'.format(sensors_observed))

    # Teach it what *didn't* happen, but which we previously thought *might* happen.
    expected_training_vectors = []
    expected_training_outcomes = []
    for oex in sensorses_expected:
      if isinstance(oex, Outcome):
        oex = oex.sensors

      if oex == sensors_observed:
        continue

      s = self.__relative_similarity(sensors_observed, oex)
      
      counterfactual_training_vector = []
      counterfactual_training_vector += sensors_prev
      counterfactual_training_vector += action
      counterfactual_training_vector += oex

      expected_training_vectors.append(counterfactual_training_vector)
      expected_training_outcomes.append(s)

      if verbosity > 0:
        print('ESTIMATOR: Counterfactual expected vector: {}  s={:.2f}'.format(oex, s))
    
    self.__neuralnet.fit(expected_training_vectors, expected_training_outcomes)



  def estimate(self, sensors_prev, action, sensors_next):
    """Compute the likelihood that, after performing action action in the context of sensor state
    sensors_prev, that the next sensor state encountered will be sensors_next.
    Arguments:
      sensors_prev {Outcome|list} -- The previous sensor vector, in which context the action was taken.
      action {Action|list} -- The action that was taken in the context of the sensors_prev sensor state.
      sensors_next {Outcome|list} -- The sensor state that might be observed after the action is taken.
    Returns:
      {float} -- The estimated relative likelihood of seeing the outcome.
    """
    # NOTE: This method may make sense to be called in bulk, with sensors_next instead being sensorses_next.
    if isinstance(sensors_prev, Outcome):
      sensors_prev = sensors_prev.sensors

    if isinstance(action, Action):
      action = action.actuators

    if isinstance(sensors_next, Outcome):
      sensors_next = sensors_next.sensors
    
    query_vector = []
    query_vector += sensors_prev
    query_vector += action
    query_vector += sensors_next

    predictions = self.__neuralnet.predict([query_vector])
    return predictions[0]








