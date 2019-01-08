
from .synapticle import Synapticle

from .utils.running_stats import RunningStats

import random

class Synaptome:
  """
  A collection of synaptons.
  """
  def __init__(self, name, synaptons, command=None):
    # The synaptome's name, for finding in the experience state index.
    self.name = name

    # The synaptons that comprise this synaptome.
    self.synaptons = set()

    # Determines whether or not this synaptome has been checked, and if so,
    # what its state was at the time at which it was checked.
    self.checkstate = None

    # How much reward this synaptome will expect to receive if it fired today.
    # Represented as a RunningStats object.
    self.expectation = RunningStats()
    self.expectation.push(0)

    # True if this synaptome was checked today, and that checking was positive.
    self.did_fire = False

    # Did the synaptome, if fired, receive its quota of reward expectation today?
    self.did_make_quota = True

    # This synaptome may optionally be linked to a command. This is the command
    # that gains candidacy if this synaptome is fulfilled.
    self.command = command

    # Keeps track of whether or not this synaptome has been flagged for various
    # recursive operations that are involved in maintenance and parsimony, such
    # as connecting to action or input atoms.
    self.flagged = False


    if isinstance(synaptons, Synapticle):
      synaptons = [synaptons]

    for s in synaptons:
      if not isinstance(s, Synapticle):
        raise ValueError('synaptons', 'Must be a collection of Synapticle objects.')
      self.add_synapton(s)
  

  def clear(self):
    self.checkstate = None
    self.flagged = False
    self.did_fire = False
    self.did_make_quota = False


  def add_random_synaptons(self, experience_state, chaining_probability=0):
    """Adds a random synapticle based on the current experience state.
    @param experience_state: Current experience state from which to draw synaptome dependencies.
    @chaining_probability: Chance of adding multiple dependencies.
    @return Self, for chaining.
    """
    sn = None
    while not sn:
      # Loops until it chooses an implemented basis.
      try:
        basis = random.choice(list(Synapticle.BASES))
        if basis == 'CHECKED':
          all_sms = experience_state.get_linkable_synaptomes()
          all_sms.discard(self)
          if not len(all_sms):
            return self

          depsm = random.choice(all_sms)
          if depsm.is_action():
            # Synaptomes that dictate an action cannot be used as a dependency.
            # The adding of synaptomes ends here.
            break

          key = depsm.name
          value = depsm.checkstate
          sn = Synapticle(basis, key, value)
      except NotImplementedError:
        sn = None
        continue

    already_has_sn = any([already_sn == sn for already_sn in self.synaptons])
    if not already_has_sn:
      self.synaptons.add(sn)

    if random.random() < chaining_probability:
      self.add_random_synaptons(experience_state, chaining_probability)



  def get_named_synaptome_dependencies(self):
    retval = set()
    for sn in self.synaptons:
      if sn.basis != 'CHECKED':
        continue
      retval.add(sn.key)
    return retval



  def is_output(self):
    return self.command is not None
    # Eventually this will include the setting of registers.


  def is_input(self):
    for sn in self.synaptons:
      if sn.basis != 'CHECKED':
        # Basically anything other than another synaptome counts as an input of some kind.
        return True
    return False


  def recursively_flag_dependencies(self, experience_state):
    """Recursively flags all synaptomes that this one is dependent on. 
    All synaptomes must have their flags cleared before this method is called.
    """
    if self.flagged:
      return
    self.flagged = True
    smnames = self.get_named_synaptome_dependencies()
    for smname in smnames:
      sm = experience_state.synaptomes.get(smname)
      if not sm:
        continue
      sm.recursively_flag_dependencies(experience_state)



  def add_synapton(self, synapticle):
    # Only add unique synaptons.
    for s in self.synaptons:
      if synapticle == s:
        return
    self.synaptons.add(synapticle)


  def is_fulfilled(self, experience_state):
    return all(sn.is_fulfilled(experience_state) for sn in self.synaptons)
      

  def decay(self, checkstate_decay_prob=0, entrenchment_decay_prob=0, entrenchment_decay_amount=1):
    if random.random() < checkstate_decay_prob:
      self.checkstate = None
      # TODO: Is this method still useful?
    

  def receive_reinforcement(self, magnitude):
    self.did_make_quota = True
    if not self.did_fire:
      return
    if self.expectation.n >= 100:
      # At some point it's fired enough times to permanently lock in,
      # and further reinforcement will change nothing.
      # This deserves tweaking.
      # TODO: Make this a settable parameter passed in from the organism.
      return

    quota_cutoff = self.expectation.mean() - 2 * self.expectation.standard_deviation()
    if magnitude < quota_cutoff:
      self.did_make_quota = False
      print('{} missed quota!'.format(self))

    self.expectation.push(magnitude)



  def __repr__(self):
    synstr = ' && '.join([str(sn) for sn in self.synaptons])
    chstr = 'T' if self.checkstate == True else 'F' if self.checkstate == False else '_'
    retval = '{}({})=<{}>'.format(self.name, chstr, synstr)
    retval += ' (+{})'.format(self.expectation)
    if self.command:
      retval += ' => "{}"'.format(self.command)
    return retval


