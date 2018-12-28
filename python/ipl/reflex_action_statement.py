

class ReflexActionStatement:
  """
  An extremely simple action statement that basically just maps
  immediate input conditions to immediate output ones.
  """
  
  def __init__(self):
    self.conditions = set()
    self.implications = set()
