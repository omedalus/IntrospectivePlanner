
class Experience:
  """A class that records a single instance of a sensor state, an action
  taken in that sensor state, the expected outcomes of that action, and the
  actual outcome.
  """

  def __init__(self, sensors_prev, actuators, sensors_observed, sensorses_expected=None):
    """Tell the estimator that a certain combination of sensors, actions, etc.,
    led to an observed outcome, and not any of the other outcomes that the estimator
    might have previously believed had high likelihoods.
    Arguments:
      sensors_prev {list} -- The previous sensor vector, in which context the action was taken.
      actuators {list} -- The action that was taken in the context of the sensors_prev sensor state.
      sensors_observed {list} -- The sensor state that was subsequently observed.
      sensorses_expected {list(list)} -- Other sensor states that weren't observed.
    """
    if not sensorses_expected:
      sensorses_expected = []

    self.sensors_prev = sensors_prev
    self.actuators = actuators
    self.sensors_observed = sensors_observed
    self.sensorses_expected = sensorses_expected


  def observed_vector(self):
    """Gets the vector of the actual observed outcome. There will be only one such vector
    in any given Experience.
    Returns:
      {list} -- The vector of the observed outcome.
    """
    v = self.sensors_prev + self.actuators + self.sensors_observed
    return v


  def training_vectors(self):
    """Get a list of training vectors and training values.
    Returns
      {(list, float)} -- A tuple of training vectors and the value to train on.
    """
    retval = []

    # Learn what actually happened.
    retval.append( (self.observed_vector(), 1) )

    # Learn all the things we thought might happen but didn't.
    for sexp in self.sensorses_expected:

      if sexp == self.sensors_observed:
        # Don't learn that it didn't happen on the one thing that *did* happen.
        continue

      retval.append( (self.sensors_prev + self.actuators + sexp, 0) )

    return retval



class ExperienceRepo:
  def __init__(self):
    """An ever-growing collection of experiences. Can be trimmed during a "sleep" phase
    to keep from getting out of hand.
    """
    self.experiences = set()


  def training_vectors(self):
    """Get a list of training vectors and training values for all experiences in the repo.
    Returns
      {(list, float)} -- A tuple of training vectors and the value to train on.
    """
    retval = []
    for experience in self.experiences:
      retval += experience.training_vectors()
    
    return retval




