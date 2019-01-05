
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

    # The number of times this synaptome has been checked. 
    # Incremented every time it's checked, regardless of whether it's found
    # to be positive or negative. This reflects its participation in the
    # regime, not its activity level per se.
    # Decays over time.
    # Affects how rewards and punishments are doled out.
    self.checkcount = 0

    # A counter that gets boosted whenever the synaptome exists while positive
    # reinforcement occurs, and decremented when pain occurs or the synaptome
    # is selected for culling. Synaptomes can only actually be culled when
    # their entrenchment reaches 0.
    self.entrenchment = 0

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
  

  def clear(self):
    self.checkcount = 0
    self.checkstate = None


  def increment_checkcount(self, increment_amt, recursion_depth=0, experience_state=None):
    self.checkcount += increment_amt
    if recursion_depth == 0:
      return
    if experience_state is None:
      raise ValueError('experience_state', 'Must be specified if recursion depth is given.')
    for sn in self.synaptons:
      if sn.basis != 'CHECKED':
        continue
      sm = experience_state.synaptomes.get(sn.key)
      if not sm:
        continue
      sm.increment_checkcount(increment_amt, recursion_depth-1, experience_state)



  def add_synapton(self, synapton):
    # Only add unique synaptons.
    for s in self.synaptons:
      if synapton == s:
        return
    self.synaptons.add(synapton)


  def is_fulfilled(self, experience_state, game_state):
    return all(sn.is_fulfilled(experience_state, game_state) for sn in self.synaptons)
      

  def decay(self, checkstate_decay_prob=0, entrenchment_decay_prob=0, entrenchment_decay_amount=1):
    if random.random() < checkstate_decay_prob:
      self.checkstate = None
      self.checkcount -= 1

    if random.random() < entrenchment_decay_prob:
      self.entrenchment -= entrenchment_decay_amount
      if self.entrenchment < 0:
        self.entrenchment = 0
    


  def __repr__(self):
    synstr = ' && '.join([str(sn) for sn in self.synaptons])
    chstr = 'T' if self.checkstate == True else 'F' if self.checkstate == False else '_'
    retval = '{}({})=<{}>'.format(self.name, chstr, synstr)
    retval += ' (x{:.2f}+{:.2f})'.format(self.entrenchment, self.checkcount)
    if self.command:
      retval += ' => "{}"'.format(self.command)
    return retval

