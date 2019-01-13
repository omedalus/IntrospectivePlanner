import numpy  # pylint: disable=E0401

class Consequence:
  def __init__(self):
    self.sensors = []

    self.estimated_relative_likelihood = None
    self.estimated_probability = None
    self.estimated_absolute_utility = 0
    self.estimated_weighted_utility = 0

    self.responses = []

  def fill_random(self, sensor_vector_dimensionality):
    # TODO: Take a ConsequenceGeneratorParams argument
    self.sensors = list(numpy.random.randint(2, size=sensor_vector_dimensionality))

  def __eq__(self, other):
    return self.sensors == other.sensors

  def __repr__(self):
    retval = 'CONSEQUENCE: '
    retval += str(self.sensors)
    retval += ' ({}% ${})'.format( int(100*self.estimated_probability), self.estimated_absolute_utility)
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
    print('Creating consequence')
    self.params = params



  def generate(self):
    """Generates a population of plausible sensor state vectors.
    Returns:
    {list} A list of Consequence objects.
    """
    population = []
    for _ in range(self.params.population_size):
      consequence = Consequence()
      consequence.fill_random(self.params.sensor_vector_dimensionality)
      if consequence in population:
        continue

      # TODO: Evaluate this consequence's likelihood with the neural network.
      consequence.estimated_relative_likelihood = 1

      population.append(consequence)

    # Normalize the likelihoods into probabilities.
    total_likelihood = sum([c.estimated_relative_likelihood for c in population])
    for c in population:
      if not total_likelihood:
        c.estimated_probability = 1.0 / len(population)
      else:
        c.estimated_probability = c.estimated_relative_likelihood / total_likelihood

    return population



