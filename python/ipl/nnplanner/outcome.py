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



  def estimate_utility(self, 
      sensors_utility_metric=None, 
      action_generator=None):
    """Compute the utility of this Outcome.
    Arguments:
      sensors_utility_metric {function} -- A function that takes a sensors vector and returns a scalar
          in the range [0,1] to describe the utility of that sensor state. If not given,
          assumes a utility of 0.
      action_generator {ActionGenerator} -- A generator that can determine what subsequent actions can be
          performed in this outcome.
    """
    if sensors_utility_metric:
      self.estimated_absolute_utility = sensors_utility_metric(self.sensors)
    else:
      self.estimated_absolute_utility = 0



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
    from .experience import Experience

    # Estimate probability
    if outcome_likelihood_estimator:
      if not with_sensors:
        raise ValueError('with_sensors', 'Must be provided if outcome_likelihood_estimator is set.')
      if not with_actuators:
        raise ValueError('with_actuators', 'Must be provided if outcome_likelihood_estimator is set.')

      experience_possible = Experience(
          with_sensors, with_actuators, self.sensors)
      y = outcome_likelihood_estimator.estimate(experience_possible)
      y = max(y, 0.0)
      y = min(y, 1.0)      

      self.estimated_relative_likelihood = y
    else:
      self.estimated_relative_likelihood = 0





  def __eq__(self, other):
    return self.sensors == other.sensors



  def __repr__(self):
    retval = 'OUTCOME: '
    retval += str(self.sensors)
    retval += ' ({:2d}% ${:.2f} = ${:.2f})'.format( 
        int(100*(self.estimated_probability or 0)), 
        self.estimated_absolute_utility or 0,
        self.estimated_weighted_utility or 0
        )
    return retval









class OutcomeGeneratorParams:
  def __init__(self, sensor_vector_dimensionality, num_generate, num_keep):
    """
    Arguments:
      sensor_vector_dimensionality {float} -- Number of elements in an action vector.
      num_generate {int} -- How many actions to generate, including repeats.
      num_keep {int} -- Of the outcomes generated, keep the top num_keep.
    """
    self.sensor_vector_dimensionality = sensor_vector_dimensionality
    self.num_generate = num_generate
    self.num_keep = num_keep
    






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
    self.action_generator = None



  def generate(self, sensors_prev, actuators):
    """Generates a population of plausible sensor state vectors.
    Returns:
    {list} A list of Outcome objects.
    """
    population = []
  
    for _ in range(self.params.num_generate):
      outcome = Outcome()
      outcome.fill_random(self.params)

      if outcome in population:
        continue
  
      outcome.estimate_likelihood(
        with_sensors=sensors_prev,
        with_actuators=actuators,
        outcome_likelihood_estimator=self.outcome_likelihood_estimator,
      )

      population.append(outcome)

    population.sort(key=lambda c: -c.estimated_relative_likelihood)
    population = population[:self.params.num_keep]

    # Normalize the likelihoods into probabilities.
    total_likelihood = sum([c.estimated_relative_likelihood for c in population])
    for c in population:
      if not total_likelihood:
        c.estimated_probability = 1.0 / len(population)
      else:
        c.estimated_probability = c.estimated_relative_likelihood / total_likelihood

    # Determine the utility of every member of the surviving population.
    for c in population:
      c.estimate_utility(
        sensors_utility_metric=self.sensors_utility_metric,
        action_generator=self.action_generator
      )
      c.estimated_weighted_utility =  c.estimated_absolute_utility * c.estimated_probability


    return population



