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



  def evaluate(self, sensors_utility_metric=None, outcome_likelihood_estimator=None, with_sensors=None, with_actuators=None):
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
    from .experience import Experience

    if sensors_utility_metric:
      self.estimated_absolute_utility = sensors_utility_metric(self.sensors)
    else:
      self.estimated_absolute_utility = 0
    
    if outcome_likelihood_estimator:
      if not with_sensors:
        raise ValueError('with_sensors', 'Must be provided if outcome_likelihood_estimator is set.')
      if not with_actuators:
        raise ValueError('with_actuators', 'Must be provided if outcome_likelihood_estimator is set.')

      experience_possible = Experience(
          with_sensors, with_actuators, self.sensors)
      y = outcome_likelihood_estimator.estimate(experience_possible)
      self.estimated_relative_likelihood = y
    else:
      self.estimated_relative_likelihood = 0



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
    self.outcome_likelihood_estimator = None



  def generate(self, sensors_prev, actuators):
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
        with_sensors=sensors_prev,
        with_actuators=actuators,
        outcome_likelihood_estimator=self.outcome_likelihood_estimator,
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



