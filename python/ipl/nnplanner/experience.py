
import math


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

    self.__total_record_count += magnitude
    situation_record.count += magnitude
    action_record.count += magnitude
    outcome_record.count += magnitude

    # Boost the salience of unlikely but actually-encountered events.
    # This is, strictly speaking, the introduction of a cognitive fallacy,
    # but it may be useful for the learning paradigm.
    # If we're adding an outcome that is currently the unlikeliest outcome
    # of this action, then boost its likelihood so that it is perceived to
    # be the next-unlikeliest.
    # NOTE: Alternatively, we can add a "curiosity flag", to indicate that
    # we suspect that it *may* happen, and we should try it more in order to
    # confirm.
    outcome_counts = sorted([oc.count for oc in action_record.outcomes.values()])
    lowest_count = outcome_counts[0]
    if outcome_record.count == lowest_count:
      outcome_counts_without_lowest = [c for c in outcome_counts if c!=lowest_count]
      if len(outcome_counts_without_lowest) > 0:
        next_lowest_count = outcome_counts_without_lowest[0]
        magboost = next_lowest_count - outcome_record.count + 1
        situation_record.count += magboost
        action_record.count += magboost
        outcome_record.count += magboost



  def get_outcome_probability(self, sensors_prev, actuators, sensors_next):
    """Gets the probability, based on direct experience, of the exact outcome occurring
    in the given situation given the described action.
    Arguments:
      sensors_prev {list} -- Sensor state.
      actuators {list} -- Action to take.
      sensors_next {list} -- Sensor state after action.
    Returns:
      {float, float} -- Probability and 95% confidence interval of the probability of
          seeing this outcome if this action is attempted in this situation.
          If the action has never been attempted before, p = 0 +/- 1
    """
    situation_key = SensorsRecord.compute_key(sensors_prev)
    action_key = ActuatorsRecord.compute_key(actuators)
    outcome_key = SensorsRecord.compute_key(sensors_next)

    situation_record = self.situations.get(situation_key)
    if not situation_record:
      return (0, 1)

    action_record = situation_record.responses.get(action_key)
    if not action_record:
      return (0, 1)
    
    outcome_record = action_record.outcomes.get(outcome_key)
    if not outcome_record:
      return (0, 1)

    p = outcome_record.count / action_record.count

    # To compute confidence interval, start with the tautology that
    # the outcome either happens or it doesn't. Treat it like a
    # Bernouli trial.
    # https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
    # https://sigmazone.com/binomial-confidence-intervals/
    z95 = 1.96
    n = action_record.count
    ci = 2 * z95 * math.sqrt ( p*(1.0-p) / n )

    # Normalize the CI range to [0,1]
    ci = min(ci, 1)

    return p, ci



  def lookup_outcomes(self, sensors, actuators, prob_threshold=0):
    """Queries for all outcomes historically observed when applying given action in given situation.
    Arguments:
      sensors {list} -- Sensor state.
      actuators {list} -- Action to take.
      prob_threshold {float} -- Don't return outcomes whose probability is below this.
    Returns:
      {list( (list, float, float) )} -- Sorted list of subsequent sensor states, with 
          probabilities and confidence intervals.
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
      # This isn't super computationally efficient, but it helps to consolidate
      # the confidence interval calculation code.
      # TODO: Factor out the confidence interval calculation code.
      prob, ci = self.get_outcome_probability(sensors, actuators, sensors_next)

      prob = outcome_record.count / action_record.count
      if prob >= prob_threshold:
        retval.append( (sensors_next, prob, ci) )

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
    
    
    
    







