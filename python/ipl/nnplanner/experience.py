

class Experience:
  """A class that records a single instance of a sensor state, an action
  taken in that sensor state, an outcome, and whether or not that outcome
  actually happened.
  """


  def __init__(self, sensors_prev, actuators, sensors_next):
    """Tell the estimator that a certain combination of sensors, actions, etc.,
    led to an observed outcome, and not any of the other outcomes that the estimator
    might have previously believed had high likelihoods.
    Arguments:
      sensors_prev {list} -- The previous sensor vector, in which context the action was taken.
      actuators {list} -- The action that was taken in the context of the sensors_prev sensor state.
      sensors_next {list} -- The sensor state that was subsequently expected and/or observed.
    """
    self.sensors_prev = sensors_prev
    self.actuators = actuators
    self.sensors_next = sensors_next


  def __repr__(self):
    retval = '{}=>{}'.format(self.reporecord_key(), self.outcome_key())
    return retval


  def reporecord_key(self):
    """A key comprised of the sensor state and action."""
    retval = ''
    retval += ''.join([str(x) for x in self.sensors_prev])
    retval += '-'
    retval += ''.join([str(x) for x in self.actuators])
    return retval


  def outcome_key(self):
    """A key comprised of the sensor state and action."""
    retval = ''
    retval += ''.join([str(x) for x in self.sensors_next])
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





class SensorsRecord:
  def __init__(self, sensors):
    self.sensors = sensors
    self.count = 0
    self.responses = {}

  def key(self):
    return SensorsRecord.compute_key(self.sensors)

  @staticmethod
  def compute_key(sensors):
    retval = ''.join([str(x) for x in sensors])
    return retval



class ActuatorsRecord:
  def __init__(self, actuators):
    self.actuators = actuators
    self.count = 0
    self.outcomes = {}

  def key(self):
    return SensorsRecord.compute_key(self.actuators)

  @staticmethod
  def compute_key(actuators):
    retval = ''.join([str(x) for x in actuators])
    return retval




class ExperienceRepo:
  def __init__(self):
    """A database of situations encountered, responses tried, and outcomes achieved.
    """
    self.situations = {}
    self.__total_record_count = 0


  def __len__(self):
    return self.__total_record_count



  def add(self, sensors_prev, actuators, sensors_observed):
    """Add several experiences to the repo.
    Arguments:
      sensors_prev {list} -- Previous sensor state.
      actuators {list} -- The action taken.
      sensors_observed {list} -- The subsequent state of the world observed.
    """
    situation_key = SensorsRecord.compute_key(sensors_prev)
    action_key = ActuatorsRecord.compute_key(actuators)
    outcome_key = SensorsRecord.compute_key(sensors_observed)

    if situation_key not in self.situations:
      self.situations[situation_key] = SensorsRecord(sensors_prev)  
    situation_record = self.situations[situation_key]

    if action_key not in situation_record.responses:
      situation_record.responses[action_key] = ActuatorsRecord(actuators)
    action_record = situation_record.responses[action_key]

    if outcome_key not in action_record.outcomes:
      action_record.outcomes[outcome_key] = SensorsRecord(sensors_observed)
    outcome_record = action_record.outcomes[outcome_key]

    self.__total_record_count += 1
    situation_record.count += 1
    action_record.count += 1
    outcome_record.count += 1








