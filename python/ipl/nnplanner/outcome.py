import numpy  # pylint: disable=E0401
import random


class Outcome:
  def __init__(self):
    self.sensors = []

    self.probability = None
    self.probability_95ci = None

    self.estimated_absolute_utility = 0
    self.estimated_weighted_utility = 0

    self.responses = []


  def probability_most_optimistic(self):
    return min(self.probability + self.probability_95ci, 1.0)


  def fill_random(self, params):
    """Populate the sensors with a random vector.
    Arguments:
      params {OutcomeGeneratorParams} -- Config object with info about how to construct the vector.
    """
    self.sensors = list(numpy.random.randint(2, size=params.sensor_vector_dimensionality))



  def estimate_utility(self, 
      sensors_utility_metric=None, 
      action_generator=None,
      lookahead_cache=None,
      recursion_depth=0,
      recursion_threshold=1):
    """Compute the utility of this Outcome.
    Arguments:
      sensors_utility_metric {function} -- A function that takes a sensors vector and returns a scalar
          in the range [0,1] to describe the utility of that sensor state. If not given,
          assumes a utility of 0.
      action_generator {ActionGenerator} -- A generator that can determine what subsequent actions can be
          performed in this outcome.
      lookahead_cache {LookaheadCache} -- A memoizer of lookahead data, to save recursion.
      recursion_depth {int} -- How deep the current recursion has gotten.
      recursion_threshold {float} -- Value between 0 and 1. Any outcomes with a utility below this level 
          will be attempted to be boosted by recursing.
    """
    if sensors_utility_metric:
      self.estimated_absolute_utility = sensors_utility_metric(self.sensors)
    else:
      self.estimated_absolute_utility = 0

    # If the utility is low, then it might still be boosted by the utility of states
    # that come afterwards.
    if self.estimated_absolute_utility < recursion_threshold:
      # First check the cache!
      cache_hit = False
      if lookahead_cache is not None:
        lh = lookahead_cache.get(self.sensors, recursion_depth)
        if lh is not None:
          cache_hit = True
          # We already know a way to get to this state, and the way we already
          # know about is at least as good as we are currently exploring.
          # Give our current exploration no credit; don't waste time on it.
          # Set it to 0 and not to lh.utility
          self.estimated_absolute_utility = 0 # lh.utility


      # If we missed the cache, but we can still recurse, then we still have a chance of
      # populating this lookahead. But it's computationally costly.
      if not cache_hit and recursion_depth > 0:
        recursed_actions = []
        try:
          recursed_actions = action_generator.generate(
              self.sensors, 
              recursion_depth=recursion_depth-1
          )
        except RecursionError:
          raise ValueError(
              'recursion_depth', "Somebody, and I'm not naming names, but SOMEBODY, forgot to enforce recursion depth limits.")

        if len(recursed_actions):
          best_action = max(recursed_actions, key=lambda a: a.expected_utility)
          self.estimated_absolute_utility = min(best_action.expected_utility, 1.0)

          if lookahead_cache is not None:
            lookahead_cache.put(self.sensors, best_action.actuators, best_action.expected_utility, recursion_depth)



  def estimate_likelihood(self, 
      outcome_likelihood_estimator=None, 
      with_sensors=None, 
      with_actuators=None):
    """Compute the likelihood of this Outcome.
    Arguments:
      outcome_likelihood_estimator {OutcomeLikelihoodEstimator} -- An object that can estimate the likelihood
          of this outcome arising from the specified action in the context of the specified
          sensor state. If not given, assumes a likelihood of 0.
      with_sensors {list} -- A sensor vector that precedes this outcome. You must provide this
          value if you want to determine this outcome's likelihood.
      with_action {list} -- An actuator vector that precedes this outcome. You must provide this
          value if you want to determine this outcome's likelihood.
    """
    # Estimate probability
    if outcome_likelihood_estimator:
      if not with_sensors:
        raise ValueError('with_sensors', 'Must be provided if outcome_likelihood_estimator is set.')
      if not with_actuators:
        raise ValueError('with_actuators', 'Must be provided if outcome_likelihood_estimator is set.')

      p, ci = outcome_likelihood_estimator.estimate(with_sensors, with_actuators, self.sensors)
      self.probability = p
      self.probability_95ci = ci
    else:
      self.probability = 0
      self.probability_95ci = 1





  def __eq__(self, other):
    return self.sensors == other.sensors



  def __repr__(self):
    retval = 'OUTCOME: '
    retval += str(self.sensors)
    retval += ' ({:2d}%±{:d}% ${:.2f} = ${:.2f})'.format( 
        int(100*(self.probability or 0)), 
        int(100*(self.probability_95ci or 0)), 
        self.estimated_absolute_utility or 0,
        self.estimated_weighted_utility or 0
        )
    return retval









class OutcomeGeneratorParams:
  def __init__(self, sensor_vector_dimensionality, num_generate, num_keep, prob_threshold, recursion_threshold):
    """
    Arguments:
      sensor_vector_dimensionality {float} -- Number of elements in an action vector.
      num_generate {int} -- How many actions to generate, including repeats.
      num_keep {int} -- Of the outcomes generated, keep the top num_keep.
      recursion_depth {int} -- How many steps forward to look, max.
      prob_threshold {float} -- Value between 0 and 1. Below this probability value, outcomes aren't even considered.
      recursion_threshold {float} -- Value between 0 and 1. Above this utility value, outcome exploration won't recurse;
          it's considered a categorical win.
    """
    self.sensor_vector_dimensionality = sensor_vector_dimensionality
    self.num_generate = num_generate
    self.num_keep = num_keep
    self.prob_threshold = prob_threshold
    self.recursion_threshold = recursion_threshold
    






class OutcomeGenerator:
  """An object that generates random sensor state vectors.
  """

  def __init__(self, organism, params, sensors_utility_metric):
    """An object that generates random sensor state vectors.
    Arguments:
      params {OutcomeGeneratorParams} -- Configuration parameters.
    """
    self.organism = organism
    self.params = params
    self.sensors_utility_metric = sensors_utility_metric



  def generate(self, sensors_prev, actuators, recursion_depth=0):
    """Generates a population of plausible sensor state vectors.
    Returns:
    {list} A list of Outcome objects.
    """
    #print('recursion_depth=', recursion_depth, ' Generating outcomes for ', sensors_prev, actuators)

    population = []
    if self.organism is not None and self.organism.outcome_likelihood_estimator is not None:
      population += self.organism.outcome_likelihood_estimator.get_known_outcomes(sensors_prev, actuators)
  
  
    for _ in range(self.params.num_generate):
      outcome = Outcome()
      outcome.fill_random(self.params)

      if outcome in population:
        continue
  
      outcome.estimate_likelihood(
        with_sensors=sensors_prev,
        with_actuators=actuators,
        outcome_likelihood_estimator=self.organism.outcome_likelihood_estimator,
      )

      population.append(outcome)

    random.shuffle(population)
    population.sort(key=lambda c: -c.probability_most_optimistic() )
    population = [c for c in population if c.probability_most_optimistic() > self.params.prob_threshold]
    population = population[:self.params.num_keep]

    #print(population)

    # Determine the utility of every member of the surviving population.
    for c in population:
      c.estimate_utility(
        sensors_utility_metric=self.sensors_utility_metric,
        action_generator=self.organism.action_generator,
        recursion_depth=recursion_depth,
        recursion_threshold=self.params.recursion_threshold,
        lookahead_cache = self.organism.lookahead_cache
      )
      # Optimism! 
      # Bias the utility estimate towards the top of the 95% confidence interval.
      c.estimated_weighted_utility = c.estimated_absolute_utility * c.probability_most_optimistic()

    # NOTE: It might be more useful to explore *some* of the utilities of lower-probability
    # outcomes. After all, a fairly low-probability outcome could have a very high utility,
    # while all other higher-probability options could have low utility.

    return population



