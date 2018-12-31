
from .synapton import Synapton


class Synaptome:
  """
  A collection of synaptons.
  """
  def __init__(self, synaptons):
    self.synaptons = set()

    if isinstance(synaptons, Synapton):
      synaptons = [synaptons]

    for s in synaptons:
      if not isinstance(s, Synapton):
        raise ValueError('synaptons', 'Must be a collection of Synapton objects.')
      self.synaptons.add(s)
  
  def add(self, basis, key=None, value=None):
    synapton = Synapton(basis, key, value)
    self.synaptons.add(synapton)
    return synapton


  def is_fulfilled(self, experience_state):
    return all(s.is_fulfilled(experience_state) for s in self.synaptons)

  def __str__(self):
    return ' && '.join([str(s) for s in self.synaptons])

