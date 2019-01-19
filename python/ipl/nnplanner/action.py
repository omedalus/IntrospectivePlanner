import numpy  # pylint: disable=E0401

class Action:
  """
  An action and possible outcomes.
  """
  def __init__(self, actuators=None):
    self.actuators = actuators or []
    self.outcomes = []
    self.expected_utility = 0


  def evaluate(self, sensors, outcome_generator, recursion_depth=0):
    """Computes the action's expected utility by examining the action's likely outcomes
    and weighing their utilities accordingly.
    Arguments:
      sensors {list} -- The context of sensor states in which this action occurs.
      outcome_generator {OutcomeGenerator} -- An object that lets us generate outcomes.
      recursion_depth {int} -- Passed along to outcome generator.
    """
    print('recursion_depth=', recursion_depth, ' Evaluating action ', sensors, self.actuators)
    self.outcomes = outcome_generator.generate(
      sensors_prev=sensors, 
      actuators=self.actuators,
      recursion_depth=recursion_depth
    )
    
    self.expected_utility = 0
    for oc in self.outcomes:
      self.expected_utility += oc.estimated_weighted_utility

    # TODO: Curiosity! Determine the max raw likelihood of the expected outcomes. If nothing
    # is likely, then we don't know what this action will do. That makes it interesting!
    # Give it a high utility.


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
    retval += ' (-> {} outcomes)'.format(len(self.outcomes))
    retval += ' ${:.02f}'.format(self.expected_utility)
    return retval



class ActionGeneratorParams:
  """An object that configures an action generator.
  """
  def __init__(self, action_vector_dimensionality, activity_level_mean, activity_level_stdev, num_generate, num_keep):
    """Configure an action generator.

    Arguments:
      action_vector_dimensionality {integer} -- Number of elements in an action vector.
      activity_level_mean {float} -- The average number of nonzero elements in the vector.
      activity_level_stdev {float} -- The standard deviation of the number of nonzero elements.
      num_generate {int} -- How many actions to generate, including repeats.
      num_keep {int} -- Of all actions generated, keep the best num_keep ones.
    """
    self.action_vector_dimensionality = action_vector_dimensionality
    self.activity_level_mean = activity_level_mean
    self.activity_level_stdev = activity_level_stdev
    self.num_generate = num_generate
    self.num_keep = num_keep


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
  def __init__(self, organism, params):
    """
    @param params: An ActionGeneratorParams object.
    """
    self.organism = organism
    self.params = params


  def generate(self, sensors, recursion_depth=0):
    """Creates a population of proposed actions.
    Arguments:
      sensors {list} -- The state of the sensors in which these actions will be taken.
    """
    print('recursion_depth=', recursion_depth, ' Generating actions for ', sensors)
    population = []
    if self.organism is not None and self.organism.outcome_likelihood_estimator is not None:
      population += self.organism.outcome_likelihood_estimator.get_known_actions(sensors)

    for _ in range(self.params.num_generate):
      action = Action()
      action.fill_random(self.params)

      if action in population:
        continue

      population.append(action)

    # DEBUGGING OVERRIDE
    if sensors[0]==1:
      population = [Action([1,0,0,0])]
    else:
      population = [Action([0,0,0,1])]


    for action in population:
      if self.organism and self.organism.outcome_generator:
        action.evaluate(
          sensors, 
          self.organism.outcome_generator, 
          recursion_depth=recursion_depth
        )

    numpy.random.shuffle(population)
    population.sort(key=lambda a: -a.expected_utility)
    population = population[:self.params.num_keep]

    return population

      


