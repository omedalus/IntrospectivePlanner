

class Lookahead:
  def __init__(self, sensors, best_actuators, utility, recursion_depth):
    self.sensors = sensors
    self.best_actuators = best_actuators
    self.utility = utility
    self.recursion_depth = recursion_depth
    # NOTE: recursion_depth is actually how much depth this path was explored to!
    # Higher means it was explored deeper.

  def key(self):
    return Lookahead.sensors_key(self.sensors)

  @staticmethod
  def sensors_key(sensors):
    retval = str(['{:.02f}'.format(x) for x in sensors])
    return retval


class LookaheadCache:
  def __init__(self):
    self.cache = {}

  def __len__(self):
    return len(self.cache)


  def clear(self):
    self.cache = {}

  def get(self, sensors, recursion_depth):
    lhkey = Lookahead.sensors_key(sensors)
    lh = self.cache.get(lhkey)
    if lh is None or recursion_depth > lh.recursion_depth:
      # If we're going to explore this path to a depth deeper than what we already did,
      # then let's go ahead and do so.
      return None
    return lh


  def put(self, sensors, actuators, utility, recursion_depth):
    lh = Lookahead(sensors, actuators, utility, recursion_depth)
    lhkey = lh.key()
    self.cache[lhkey] = lh

 
