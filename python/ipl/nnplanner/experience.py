

class Experience:
  """A class that records a single instance of a sensor state, an action
  taken in that sensor state, an outcome, and whether or not that outcome
  actually happened.
  """


  def __init__(self, sensors_prev, actuators, sensors_next, happened=None):
    """Tell the estimator that a certain combination of sensors, actions, etc.,
    led to an observed outcome, and not any of the other outcomes that the estimator
    might have previously believed had high likelihoods.
    Arguments:
      sensors_prev {list} -- The previous sensor vector, in which context the action was taken.
      actuators {list} -- The action that was taken in the context of the sensors_prev sensor state.
      sensors_next {list} -- The sensor state that was subsequently expected and/or observed.
      happened {Boolean} -- Did the experience actually happen, or was it a counterfactual expectation?
          Leave as None for a hypothetical experience whose outcome hasn't been observed yet.
    """
    self.sensors_prev = sensors_prev
    self.actuators = actuators
    self.sensors_next = sensors_next
    self.happened = happened

  def __repr__(self):
    retval = ''
    retval += ''.join([str(x) for x in self.sensors_prev])
    retval += '-'
    retval += ''.join([str(x) for x in self.actuators])
    retval += '-'
    retval += ''.join([str(x) for x in self.sensors_next])
    retval += '-'
    retval += '1' if self.happened else '?' if self.happened is None else '0'
    return retval


  def vector(self):
    """The full experience described as a vector for use as input to the estimator.
    Returns:
      {list} -- A concatenated vector of all of this experience's components.
    """
    retval = []
    retval += self.sensors_prev
    retval += self.actuators
    retval += self.sensors_next
    return retval



  def training_vector(self):
    """Get a vector to train the estimator on.
    Returns
      {(list, float)} -- A tuple of the vector and the value to train on.
    """
    if self.happened is None:
      raise ValueError("Can't build training vector from an experience that hasn't happened yet.")

    retval = ( (self.vector(), 1 if self.happened else 0) )
    return retval



class ExperienceRepo:
  def __init__(self):
    """An ever-growing collection of experiences. Can be trimmed during a "sleep" phase
    to keep from getting out of hand.
    """
    self.experiences = set()


  def __len__(self):
    return len(self.experiences)



  def add(self, sensors_prev, actuators, sensors_observed, sensorses_expected):
    """Add several experiences to the repo.
    Arguments:
      sensors_prev {list} -- Previous sensor state.
      actuators {list} -- The action taken.
      sensors_observed {list} -- The subsequent state of the world observed.
      sensorses_expected {list(list)} -- Possible states of the world that weren't observed.
    """
    self.experiences.add(Experience(sensors_prev, actuators, sensors_observed, True))
    for sexp in sensorses_expected:
      if sexp == sensors_observed:
        continue
      self.experiences.add(Experience(sensors_prev, actuators, sexp, False))


  def remove(self, without=[]):
    """Removes experiences from the repo.
    Arguments
      without {list} -- Collection of Experiences to exclude from the output.
    """
    try:
      iter(without)
    except TypeError:
      without = [without]

    for experience in without:
      self.experiences.discard(experience)



  def training_data(self, without=[]):
    """Get a list of training vectors and training values for all experiences in the repo.
    Arguments
      without {list} -- Collection of Experiences to exclude from the output.
    Returns
      {(list(list), list(float))} -- A tuple of training vectors and the values to train on.
    """
    try:
      iter(without)
    except TypeError:
      without = [without]

    tvecsX = []
    tvecsY = []
    for experience in self.experiences:
      if experience in without:
        continue
      tv = experience.training_vector()
      tvecsX.append(tv[0])
      tvecsY.append(tv[1])
    
    retval = (tvecsX, tvecsY)
    return retval




