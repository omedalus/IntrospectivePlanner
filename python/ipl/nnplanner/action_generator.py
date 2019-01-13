import numpy  # pylint: disable=E0401

class ActionGeneratorParams:
  """
  An object that configures an action generator.
  """
  def __init__(self, action_vector_dimensionality, activity_level_mean, activity_level_stdev, population_size):
    """
    @param action_vector_dimensionality: Number of elements in an action vector.
    @param activity_level_mean: The average number of nonzero elements in the vector.
    @param activity_level_stdev: The standard deviation of the number of nonzero elements.
    @param population_size: How many actions to generate, including repeats.
    """
    self.action_vector_dimensionality = action_vector_dimensionality
    self.activity_level_mean = activity_level_mean
    self.activity_level_stdev = activity_level_stdev
    self.population_size = population_size


class ActionGenerator:
  """
  An object that generates random action vectors.

  Action vectors are currently strictly Boolean,
  with each element being only 0 or 1. In the future,
  we may use continuous action states. In either case,
  it's assumed that the activity vector is sparse; 
  only a few elements are 1, while the rest are 0.

  The generator uses a genetic algorithm to evaluate
  actions for viability and desirability.
  """
  def __init__(self, params):
    """
    @param params: An ActionGeneratorParams object.
    """
    self.params = params
    self.population = []
    self.selected_action = None


  def __generate_one(self):
    """
    Generate one action vector.
    """
    retval = [0] * self.params.action_vector_dimensionality

    nactive = numpy.random.normal(self.params.activity_level_mean, self.params.activity_level_stdev)
    if nactive < 0:
      nactive = 0
    nactive = int(nactive)
    if nactive >= self.params.action_vector_dimensionality:
      nactive = self.params.action_vector_dimensionality

    indices = numpy.random.choice(self.params.action_vector_dimensionality, nactive, False)
    for index in indices:
      retval[index] = 1
    return retval
    

  def generate(self):
    """
    Creates a population of proposed actions.
    """
    self.population = []
    self.selected_action = None
    for _ in range(self.params.population_size):
      newvec = self.__generate_one()
      if any([newvec == v for v in self.population]):
        continue
      self.population.append(newvec)
    
    ia = numpy.random.choice(len(self.population))
    self.selected_action = self.population[ia]
      


