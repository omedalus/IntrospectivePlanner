
from .synapton import Synapton


class Synaptome:
  """
  A collection of synaptons.
  """
  def __init__(self, name, synaptons):
    self.name = name
    self.synaptons = set()

    # A counter that gets boosted whenever the synaptome exists while positive
    # reinforcement occurs, and decremented when pain occurs or the synaptome
    # is selected for culling. Synaptomes can only actually be culled when
    # their entrenchment reaches 0.
    self.entrenchment = 0


    if isinstance(synaptons, Synapton):
      synaptons = [synaptons]

    for s in synaptons:
      if not isinstance(s, Synapton):
        raise ValueError('synaptons', 'Must be a collection of Synapton objects.')
      self.add_synapton(s)
  

  def add(self, basis, key=None, value=None):
    synapton = Synapton(basis, key, value)
    self.add_synapton(synapton)
    return synapton


  def add_synapton(self, synapton):
    # Only add unique synaptons.
    for s in self.synaptons:
      if synapton == s:
        return
    self.synaptons.add(synapton)


  def is_fulfilled(self, experience_state, game_state):
    return all(s.is_fulfilled(experience_state, game_state) for s in self.synaptons)

  def __repr__(self):
    synstr = ' && '.join([str(s) for s in self.synaptons])
    retval = self.name + '=<' + synstr + '>'
    return retval

