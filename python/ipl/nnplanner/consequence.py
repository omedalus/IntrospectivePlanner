import numpy  # pylint: disable=E0401

class Consequence:
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
      params {ConsequenceGeneratorParams} -- Config object with info about how to construct the vector.
    """
    self.sensors = list(numpy.random.randint(2, size=params.sensor_vector_dimensionality))

  def evaluate(self, sensors_utility_metric=None, consequence_likelihood_estimator=None, with_sensors=None, with_action=None):
    """Compute the likelihood and utility of this Consequence.
    Arguments:
      sensors_utility_metric {function} -- A function that takes a sensors vector and returns a scalar
          in the range [0,1] to describe the utility of that sensor state. If not given,
          assumes a utility of 0.
      consequence_likelihood_estimator {MLPRegressor} -- An object that can estimate the likelihood
          of this consequence arising from the specified action in the context of the specified
          sensor state. If not given, assumes a likelihood of 0.
      with_sensors {list} -- A sensor vector that precedes this consequence. You must provide this
          value if you want to determine this consequence's likelihood.
      with_action {list} -- An actuator vector that precedes this consequence. You must provide this
          value if you want to determine this consequence's likelihood.
    """
    if sensors_utility_metric:
      self.estimated_absolute_utility = sensors_utility_metric(self.sensors)
    else:
      self.estimated_absolute_utility = 0
    
    if consequence_likelihood_estimator:
      if not with_sensors:
        raise ValueError('with_sensors', 'Must be provided if consequence_likelihood_estimator is set.')
      if not with_action:
        raise ValueError('with_action', 'Must be provided if consequence_likelihood_estimator is set.')
      v = []
      v += with_sensors
      v += with_action
      v += self.sensors
      y = consequence_likelihood_estimator.predict(v)
      self.estimated_relative_likelihood = y[0]
    else:
      self.estimated_relative_likelihood = 0



  def __eq__(self, other):
    return self.sensors == other.sensors

  def __repr__(self):
    retval = 'CONSEQUENCE: '
    retval += str(self.sensors)
    retval += ' ({}% ${:.2f} = ${:.2f})'.format( 
        int(100*self.estimated_probability), 
        self.estimated_absolute_utility,
        self.estimated_weighted_utility
        )
    return retval



class ConsequenceGeneratorParams:
  def __init__(self, sensor_vector_dimensionality, population_size):
    """
    @param sensor_vector_dimensionality: Number of elements in an action vector.
    @param population_size: How many actions to generate, including repeats.
    """
    self.sensor_vector_dimensionality = sensor_vector_dimensionality
    self.population_size = population_size
    

class ConsequenceGenerator:
  """An object that generates random sensor state vectors.
  """

  def __init__(self, params):
    """An object that generates random sensor state vectors.
    Arguments:
      params {ConsequenceGeneratorParams} -- Configuration parameters.
    """
    self.params = params
    self.sensors_utility_metric = None



  def generate(self):
    """Generates a population of plausible sensor state vectors.
    Returns:
    {list} A list of Consequence objects.
    """
    population = []
    for _ in range(self.params.population_size):
      consequence = Consequence()
      consequence.fill_random(self.params)
      if consequence in population:
        continue

      consequence.evaluate(
        sensors_utility_metric=self.sensors_utility_metric
      )

      population.append(consequence)

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



