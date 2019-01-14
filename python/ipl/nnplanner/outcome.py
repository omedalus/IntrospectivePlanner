import numpy  # pylint: disable=E0401



class Outcome:
  def __init__(self):
    self.sensors = []

    self.estimated_relative_likelihood = None
    self.estimated_absolute_utility = 0

    self.estimated_probability = None
    self.estimated_weighted_utility = 0

    self.responses = []



  def fill_random(self, params):
    """Populate the sensors with a random vector.
    Arguments:
      params {OutcomeGeneratorParams} -- Config object with info about how to construct the vector.
    """
    self.sensors = list(numpy.random.randint(2, size=params.sensor_vector_dimensionality))



  def evaluate(self, sensors_utility_metric=None, outcome_likelihood_estimator=None, with_sensors=None, with_action=None):
    """Compute the likelihood and utility of this Outcome.
    Arguments:
      sensors_utility_metric {function} -- A function that takes a sensors vector and returns a scalar
          in the range [0,1] to describe the utility of that sensor state. If not given,
          assumes a utility of 0.
      outcome_likelihood_estimator {MLPRegressor} -- An object that can estimate the likelihood
          of this outcome arising from the specified action in the context of the specified
          sensor state. If not given, assumes a likelihood of 0.
      with_sensors {list} -- A sensor vector that precedes this outcome. You must provide this
          value if you want to determine this outcome's likelihood.
      with_action {list} -- An actuator vector that precedes this outcome. You must provide this
          value if you want to determine this outcome's likelihood.
    """
    if sensors_utility_metric:
      self.estimated_absolute_utility = sensors_utility_metric(self.sensors)
    else:
      self.estimated_absolute_utility = 0
    
    if outcome_likelihood_estimator:
      if not with_sensors:
        raise ValueError('with_sensors', 'Must be provided if outcome_likelihood_estimator is set.')
      if not with_action:
        raise ValueError('with_action', 'Must be provided if outcome_likelihood_estimator is set.')
      v = []
      v += with_sensors
      v += with_action
      v += self.sensors
      y = outcome_likelihood_estimator.predict(v)
      self.estimated_relative_likelihood = y[0]
    else:
      self.estimated_relative_likelihood = 0


    def relative_similarity(self, comp_sensors):
      """Compute the proximity of this outcome's sensor vector to the given one.
      Arguments:
        comp_sensors {list} -- A sensor vector to compare against.
      Returns:
        {float} -- A float between 0 and 1, where 1 means the two vectors are identical 
            and 0 means the two vectors differ by at least .5 in every element. 
      """
      if len(comp_sensors) != len(self.sensors):
        raise ValueError('comp_sensor array needs to be the same length as self.sensors')

      # This is just a const that tells us how different we permit two different
      # sensor values to be before we give no reward at all for the counterfactual
      # one. By setting it to <=.5, we can ensure that the trainee can't "cheat" by
      # always outputting exactly .5 and always getting partial credit regardless of
      # if the desired value is 0 or 1.
      max_piecewise_diff = .5

      # I could do something cleverly Pythonic here, but I'd really rather make
      # the math explicit and obvious to make coding and debugging easier.
      total_prox = 0
      for ms, cs in zip(self.sensors, comp_sensors):
        abs_diff = abs(ms - cs)
        magnified_diff = abs_diff / max_piecewise_diff
        truncated_magnified_diff = min(magnified_diff, 1)
        prox = 1 - truncated_magnified_diff
        total_prox += prox

      normalized_prox = total_prox / len(self.sensors)
      return normalized_prox


  def __eq__(self, other):
    return self.sensors == other.sensors



  def __repr__(self):
    retval = 'OUTCOME: '
    retval += str(self.sensors)
    retval += ' ({}% ${:.2f} = ${:.2f})'.format( 
        int(100*self.estimated_probability), 
        self.estimated_absolute_utility,
        self.estimated_weighted_utility
        )
    return retval









class OutcomeGeneratorParams:
  def __init__(self, sensor_vector_dimensionality, population_size):
    """
    @param sensor_vector_dimensionality: Number of elements in an action vector.
    @param population_size: How many actions to generate, including repeats.
    """
    self.sensor_vector_dimensionality = sensor_vector_dimensionality
    self.population_size = population_size
    






class OutcomeGenerator:
  """An object that generates random sensor state vectors.
  """

  def __init__(self, params):
    """An object that generates random sensor state vectors.
    Arguments:
      params {OutcomeGeneratorParams} -- Configuration parameters.
    """
    self.params = params
    self.sensors_utility_metric = None



  def generate(self):
    """Generates a population of plausible sensor state vectors.
    Returns:
    {list} A list of Outcome objects.
    """
    population = []
    for _ in range(self.params.population_size):
      outcome = Outcome()
      outcome.fill_random(self.params)
      if outcome in population:
        continue

      outcome.evaluate(
        sensors_utility_metric=self.sensors_utility_metric
      )

      population.append(outcome)

    # Normalize the likelihoods into probabilities.
    total_likelihood = sum([c.estimated_relative_likelihood for c in population])
    for c in population:
      if not total_likelihood:
        c.estimated_probability = 1.0 / len(population)
      else:
        c.estimated_probability = c.estimated_relative_likelihood / total_likelihood
    for c in population:
      c.estimated_weighted_utility =  c.estimated_absolute_utility * c.estimated_probability

    return population



