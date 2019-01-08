
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

    # This synaptome may optionally be linked to a command. This is the command
    # that gains candidacy if this synaptome is fulfilled.
    self.command = command

    # Keeps track of whether or not this synaptome has been flagged for various
    # recursive operations that are involved in maintenance and parsimony, such
    # as connecting to action or input atoms.
    self.flagged = False


    if isinstance(synaptons, Synapton):
      synaptons = [synaptons]

    for s in synaptons:
      if not isinstance(s, Synapton):
        raise ValueError('synaptons', 'Must be a collection of Synapton objects.')
      self.add_synapton(s)
  

  def clear(self):
    self.checkstate = None
    self.flagged = False


  def add_random_synaptons(self, experience_state, chaining_probability=0):
    """Adds a random synapton based on the current experience state.
    @param experience_state: Current experience state from which to draw synaptome dependencies.
    @chaining_probability: Chance of adding multiple dependencies.
    @return Self, for chaining.
    """
    sn = None
    while not sn:
      # Loops until it chooses an implemented basis.
      try:
        basis = random.choice(list(Synapton.BASES))
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
          sn = Synapton(basis, key, value)
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



  def add_synapton(self, synapton):
    # Only add unique synaptons.
    for s in self.synaptons:
      if synapton == s:
        return
    self.synaptons.add(synapton)


  def is_fulfilled(self, experience_state):
    return all(sn.is_fulfilled(experience_state) for sn in self.synaptons)
      

  def decay(self, checkstate_decay_prob=0, entrenchment_decay_prob=0, entrenchment_decay_amount=1):
    if random.random() < checkstate_decay_prob:
      self.checkstate = None

    if random.random() < entrenchment_decay_prob:
      self.entrenchment -= entrenchment_decay_amount
      if self.entrenchment < 0:
        self.entrenchment = 0
    


  def __repr__(self):
    synstr = ' && '.join([str(sn) for sn in self.synaptons])
    chstr = 'T' if self.checkstate == True else 'F' if self.checkstate == False else '_'
    retval = '{}({})=<{}>'.format(self.name, chstr, synstr)
    retval += ' (x{:.2f})'.format(self.entrenchment)
    if self.command:
      retval += ' => "{}"'.format(self.command)
    return retval

