import numpy  # pylint: disable=E0401

class Consequence:
  def __init__(self):
    self.sensors = []
    self.estimated_probability = 0
    self.responses = []


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



