

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



  def add(self, sensors_prev, actuators, sensors_observed, magnitude=1):
    """Add several experiences to the repo.
    Arguments:
      sensors_prev {list} -- Previous sensor state.
      actuators {list} -- The action taken.
      sensors_observed {list} -- The subsequent state of the world observed.
    """
    situation_key = SensorsRecord.compute_key(sensors_prev)
    action_key = ActuatorsRecord.compute_key(actuators)
    outcome_key = SensorsRecord.compute_key(sensors_observed)

    new_situation = False
    new_action = False
    new_outcome = False

    if situation_key not in self.situations:
      self.situations[situation_key] = SensorsRecord(sensors_prev)  
    situation_record = self.situations[situation_key]

    if action_key not in situation_record.responses:
      situation_record.responses[action_key] = ActuatorsRecord(actuators)
    action_record = situation_record.responses[action_key]

    if outcome_key not in action_record.outcomes:
      action_record.outcomes[outcome_key] = SensorsRecord(sensors_observed)
    outcome_record = action_record.outcomes[outcome_key]

    # Make the salience of new experiences proportional to prior experience magnitudes.

    # If it's an old action in an old situation but produces a new outcome,
    # that's extremely interesting!
    if not new_situation and not new_action and new_outcome:
      magnitude += len(self)

    self.__total_record_count += magnitude
    situation_record.count += magnitude
    action_record.count += magnitude
    outcome_record.count += magnitude



  def get_outcome_probability(self, sensors_prev, actuators, sensors_next):
    """Gets the probability, based on direct experience, of the exact outcome occurring
    in the given situation given the described action.
    Arguments:
      sensors_prev {list} -- Sensor state.
      actuators {list} -- Action to take.
      sensors_next {list} -- Sensor state after action.
    Returns:
      {float} -- Probability of seeing the outcome result, or None if the action has
          never been attempted in this situation before.
    """
    situation_key = SensorsRecord.compute_key(sensors_prev)
    action_key = ActuatorsRecord.compute_key(actuators)
    outcome_key = SensorsRecord.compute_key(sensors_next)

    situation_record = self.situations.get(situation_key)
    if not situation_record:
      return None

    action_record = situation_record.responses.get(action_key)
    if not action_record:
      return None
    
    outcome_record = action_record.outcomes.get(outcome_key)
    if not outcome_record:
      return 0

    return outcome_record.count / action_record.count



  def lookup_outcomes(self, sensors, actuators, prob_threshold=0):
    """Queries for all outcomes historically observed when applying given action in given situation.
    Arguments:
      sensors {list} -- Sensor state.
      actuators {list} -- Action to take.
      prob_threshold {float} -- Don't return outcomes whose probability is below this.
    Returns:
      {list( (list, float) )} -- Sorted list of subsequent sensor states, with probabilities.
    """
    situation_key = SensorsRecord.compute_key(sensors)
    action_key = ActuatorsRecord.compute_key(actuators)

    situation_record = self.situations.get(situation_key)
    if not situation_record:
      return []

    action_record = situation_record.responses.get(action_key)
    if not action_record:
      return []
    
    retval = []
    for outcome_record in action_record.outcomes.values():
      sensors_next = outcome_record.sensors
      prob = outcome_record.count / action_record.count
      if prob >= prob_threshold:
        retval.append( (sensors_next, prob) )

    retval.sort(key = lambda x: -x[1])
    return retval


  def lookup_actions(self, sensors):
    """Queries for all actions that had been attempted before in this situation.
    Arguments:
      sensors {list} -- Sensor state.
    Returns:
      {list(list)} -- List of action vectors.
    """
    situation_key = SensorsRecord.compute_key(sensors)
    situation_record = self.situations.get(situation_key)
    if not situation_record:
      return []

    retval = []
    for action_record in situation_record.responses.values():
      retval.append(action_record.actuators)

    return retval
    
    
    
    







