import numpy  # pylint: disable=E0401

class Action:
  """
  An action and possible consequences.
  """
  def __init__(self):
    self.actuators = []
    self.consequences = []
    self.expected_utility = 0


  def evaluate(self, consequence_generator):
    """Computes the action's expected utility by examining the action's likely outcomes
    and weighing their utilities accordingly.
    Arguments:
      consequence_generator {ConsequenceGenerator} -- An object that lets us generate consequences.
    """
    self.consequences = consequence_generator.generate()
    
    # TODO: Action's utility is the weighted sum of the utilities of 
    # all of its expected consequences.


  def fill_random(self, params):
    """Fill the action vector based on the configuration of an action generator.
    Arguments:
      params {ActionGeneratorParams} -- Describes how to create this vector.
    """
    self.actuators = [0] * params.action_vector_dimensionality

    nactive = numpy.random.normal(
        params.activity_level_mean, params.activity_level_stdev)
    if nactive < 0:
      nactive = 0
    nactive = int(nactive)
    if nactive >= params.action_vector_dimensionality:
      nactive = params.action_vector_dimensionality

    indices = numpy.random.choice(
        params.action_vector_dimensionality, nactive, False)
    for index in indices:
      self.actuators[index] = 1


  def __eq__(self, other):
    return self.actuators == other.actuators

  def __repr__(self):
    retval = 'ACTION: '
    retval += str(self.actuators)
    retval += ' (-> {} consequences)'.format(len(self.consequences))
    return retval



class ActionGeneratorParams:
  """An object that configures an action generator.
  """
  def __init__(self, action_vector_dimensionality, activity_level_mean, activity_level_stdev, population_size):
    """Configure an action generator.

    Arguments:
      action_vector_dimensionality {integer} -- Number of elements in an action vector.
      activity_level_mean {float} -- The average number of nonzero elements in the vector.
      activity_level_stdev {float} -- The standard deviation of the number of nonzero elements.
      population_size {int} -- How many actions to generate, including repeats.
    """
    self.action_vector_dimensionality = action_vector_dimensionality
    self.activity_level_mean = activity_level_mean
    self.activity_level_stdev = activity_level_stdev
    self.population_size = population_size


class ActionGenerator:
  """Generates random action vectors.

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
    self.consequence_generator = None


  def generate(self):
    """
    Creates a population of proposed actions.
    """
    population = []
    self.selected_action = None
    for _ in range(self.params.population_size):
      action = Action()
      action.fill_random(self.params)

      if action in population:
        continue

      if self.consequence_generator:
        action.evaluate(self.consequence_generator)


      population.append(action)

    return population

      


