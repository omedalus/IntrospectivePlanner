

class Lookahead:
  def __init__(self, sensors, best_actuators, utility):
    self.sensors = sensors
    self.best_actuators = best_actuators
    self.utility = utility

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

  def get(self, sensors):
    lhkey = Lookahead.sensors_key(sensors)
    return self.cache.get(lhkey)

  def put(self, sensors, actuators, utility):
    lh = Lookahead(sensors, actuators, utility)
    lhkey = lh.key()
    self.cache[lhkey] = lh

 
