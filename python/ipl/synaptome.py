
from .synapton import Synapton

import random

class Synaptome:
  """
  A collection of synaptons.
  """
  def __init__(self, name, synaptons, command=None, inhibit=None):
    # The synaptome's name, for finding in the experience state index.
    self.name = name

    # The synaptons that comprise this synaptome.
    self.synaptons = set()

    # Determines whether or not this synaptome has been checked, and if so,
    # what its state was at the time at which it was checked.
    self.checkstate = None

    # A counter that gets boosted whenever the synaptome exists while positive
    # reinforcement occurs, and decremented when pain occurs or the synaptome
    # is selected for culling. Synaptomes can only actually be culled when
    # their entrenchment reaches 0.
    self.entrenchment = 0

    # A counter that gets boosted every time another synaptome checks this one,
    # or this synaptome's action gets performed. A synaptome's portion of the
    # payout is partly determined by how many citations it's received.
    self.citation_count = 0

    # This synaptome may optionally be linked to a command. This is the command
    # that gains candidacy if this synaptome is fulfilled.
    self.command = command

    # This synaptome may optionally inhibit another synaptome. If so, it removes
    # the inhibited synaptome's check from the Checked collection.
    # NOTE: This isn't a thing yet.
    self.inhibit = inhibit


    if isinstance(synaptons, Synapton):
      synaptons = [synaptons]

    for s in synaptons:
      if not isinstance(s, Synapton):
        raise ValueError('synaptons', 'Must be a collection of Synapton objects.')
      self.add_synapton(s)
  


  def add_synapton(self, synapton):
    # Only add unique synaptons.
    for s in self.synaptons:
      if synapton == s:
        return
    self.synaptons.add(synapton)


  def is_fulfilled(self, experience_state, game_state):
    return all(sn.is_fulfilled(experience_state, game_state) for sn in self.synaptons)


  def increment_citation_with_backpropagation(self,  experience_state):
    """Increments the citation of this synaptome and all of its immediate dependencies. Does not recurse.
    """
    self.citation_count += 1
    for sn in self.synaptons:
      if sn.basis != 'CHECKED':
        continue
      sm = experience_state.synaptomes.get(sn.key)
      if not sm:
        continue
      sm.citation_count += 1
      

  def decay(self, checkstate_decay_prob=0, entrenchment_decay_prob=0, citation_decay_prob=0):
    if random.random() < checkstate_decay_prob:
      self.checkstate = None

    if self.entrenchment > 0 and random.random() < entrenchment_decay_prob:
      #self.entrenchment *= random.random()
      self.entrenchment -= 1
      if self.entrenchment < 0:
        self.entrenchment = 0

    if self.citation_count > 0 and random.random() < citation_decay_prob:
      #self.citation_count *= random.random()
      self.citation_count -= 1
      if self.citation_count < 0:
        self.citation_count = 0
    


  def __repr__(self):
    synstr = ' && '.join([str(sn) for sn in self.synaptons])
    chstr = 'T' if self.checkstate == True else 'F' if self.checkstate == False else '_'
    retval = '{}({})(+{})=<{}>'.format(self.name, chstr, self.citation_count, synstr)
    retval += ' (x{})'.format(self.entrenchment)
    if self.command:
      retval += ' => "{}"'.format(self.command)
    return retval

