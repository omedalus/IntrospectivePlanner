
from .synapticle import Synapticle

from .utils.running_stats import RunningStats

import random

class Synapton:
  """
  A collection of synapticles.
  """
  def __init__(self, name, synapticles=None, command=None):
    # The synapton's name, for finding in the experience state index.
    self.name = name

    # The synapticles that comprise this synapton.
    self.synapticles = set()

    # Determines whether or not this synapton has been checked, and if so,
    # what its state was at the time at which it was checked.
    self.checkstate = None

    # How much reward this synapton will expect to receive if it fired today.
    # Represented as a RunningStats object.
    self.expectation = RunningStats()
    self.expectation.push(0)

    # True if this synapton was checked today, and that checking was positive.
    self.did_fire = False

    # Did the synapton, if fired, receive its quota of reward expectation today?
    # TODO: Someday maybe this will be a metric of, say, how many standard deviations
    # the quota was missed by. For now, it doesn't matter.
    self.did_make_quota = True

    # This synapton may optionally be linked to a command. This is the command
    # that gains candidacy if this synapton is fulfilled.
    self.command = command

    # Keeps track of whether or not this synapton has been flagged for various
    # recursive operations that are involved in maintenance and parsimony, such
    # as connecting to action or input atoms.
    self.flagged = False

    # Is this synapton checkable? When we play a game, we want to test the entire
    # cohort of synaptons that are determining the play of that game. Therefore,
    # synaptons created midway during play shouldn't count until after the game
    # is done.
    self.is_tentative = True

    if not synapticles:
      synapticles = []

    if isinstance(synapticles, Synapticle):
      synapticles = [synapticles]

    for s in synapticles:
      if not isinstance(s, Synapticle):
        raise ValueError('synapticles', 'Must be a collection of Synapticle objects.')
      self.add_synapticle(s)
  

  def clear(self):
    self.checkstate = None
    self.flagged = False
    self.did_fire = False
    self.did_make_quota = False
    self.is_tentative = False


  def add_random_synapticles(self, experience_state, chaining_probability=0):
    """Adds a random synapticle based on the current experience state.
    @param experience_state: Current experience state from which to draw synapton dependencies.
    @chaining_probability: Chance of adding multiple dependencies.
    @return Self, for chaining.
    """
    sicl = None
    while not sicl:
      # Loops until it chooses an implemented basis.
      try:
        basis = random.choice(list(Synapticle.BASES))
        if basis == 'CHECKED':
          all_sms = experience_state.get_linkable_synaptons()
          all_sms.discard(self)
          if not len(all_sms):
            return self

          depsm = random.choice(list(all_sms))
          if depsm.is_output():
            # Synaptomes that dictate an action cannot be used as a dependency.
            # The adding of synaptons ends here.
            break

          key = depsm.name
          value = depsm.checkstate
          sicl = Synapticle(basis, key, value)
      except NotImplementedError:
        sicl = None
        continue

    self.add_synapticle(sicl)
    if random.random() < chaining_probability:
      self.add_random_synapticles(experience_state, chaining_probability)



  def get_named_synapton_dependencies(self):
    retval = set()
    for sicl in self.synapticles:
      if sicl.basis != 'CHECKED':
        continue
      retval.add(sicl.key)
    return retval



  def is_output(self):
    return self.command is not None
    # Eventually this will include the setting of registers.


  def is_input(self):
    for sicl in self.synapticles:
      if sicl.basis != 'CHECKED':
        # Basically anything other than another synapton counts as an input of some kind.
        return True
    return False


  def recursively_flag_dependencies(self, experience_state):
    """Recursively flags all synaptons that this one is dependent on. 
    All synaptons must have their flags cleared before this method is called.
    """
    if self.flagged:
      return
    self.flagged = True
    smnames = self.get_named_synapton_dependencies()
    for smname in smnames:
      sn = experience_state.synaptons.get(smname)
      if not sn:
        continue
      sn.recursively_flag_dependencies(experience_state)



  def add_synapticle(self, synapticle):
    # Only add unique synapticles.
    for s in self.synapticles:
      if synapticle == s:
        return
    self.synapticles.add(synapticle)


  def is_fulfilled(self, experience_state):
    return all(sicl.is_fulfilled(experience_state) for sicl in self.synapticles)
          

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
    synstr = ' && '.join([str(sicl) for sicl in self.synapticles])
    chstr = 'T' if self.checkstate == True else 'F' if self.checkstate == False else '_'
    retval = '{}({})=<{}>'.format(self.name, chstr, synstr)
    retval += ' (+{})'.format(self.expectation)
    if self.command:
      retval += ' => "{}"'.format(self.command)
    if not self.did_make_quota:
      retval = 'X-' + retval
    if self.is_tentative:
      retval = '...' + retval
    return retval



