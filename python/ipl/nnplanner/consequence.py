import numpy  # pylint: disable=E0401

class Consequence:
  def __init__(self):
    self.sensors = []
    self.estimated_probability = None
    self.estimated_relative_likelihood = None
    self.responses = []

  def fill_random(self, sensor_vector_dimensionality):
    self.sensors = numpy.random.randint(2, sensor_vector_dimensionality)

  def __eq__(self, other):
    return self.sensors == other.sensors

  def __repr__(self):
    retval = 'CONSEQUENCE: '
    retval += str(self.sensors)
    retval += ' ({:.2f})'.format(self.estimated_probability)
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
  """
  An object that generates random sensor state vectors.
  """

  def __init__(self, params):
    """
    @param params: A ConsequenceGeneratorParams object.
    """
    self.params = params
    self.population = []



  def generate(self):
    """
    Generates a bunch of plausible actions.
    """
    self.population = []
    for _ in self.params.population_size:
      consequence = Consequence()
      consequence.fill_random(self.params.sensor_vector_dimensionality)
      if consequence in self.population:
        continue

      # TODO: Evaluate this consequence's likelihood with the neural network.
      consequence.estimated_relative_likelihood = 1

    # Normalize the likelihoods into probabilities.
    total_likelihood = sum([c.estimated_relative_likelihood for c in self.population])
    for c in self.population:
      if not total_likelihood:
        c.estimated_probability = 1.0 / len(self.population)
      else:
        c.estimated_probability = c.estimated_relative_likelihood / total_likelihood




