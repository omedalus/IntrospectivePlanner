
import random
import statistics

class ExperienceState:
  """
  An object that describes the total state of the organism
  at any given time. This includes inputs from the outside
  world, inputs from its own body (if any), the current
  state of any internal "cognitive registers" or mental
  "notes" that it may be putting into its own "working
  memory", and also the current ruleset by which it determines
  how its actions will cause its subsequent experiences to
  evolve.
  """


  def __init__(self):
    # The most recent command that the organism sent to the game.
    self.last_command = None

    # Collection of named atoms that are currently being experienced 
    # by the organism. 
    self.inputs = set()

    # A map of named synaptons. Synaptomes get checked against
    # an existing experience state, so checking them is a free action.
    # NOTE: Maybe the organism can choose to check a named synapton,
    # or maybe checking synaptons is itself an action.
    self.synaptons = {}
    

  def __repr__(self):
    retval = '\tLast command: {}\n'.format(self.last_command)
    retval += '\tSynaptomes:\n'

    sms = list([sn for sn in self.synaptons.values()])
    sms.sort(key = lambda sn: -sn.entrenchment)

    for sn in sms:
      retval += '\t\t{}\n'.format(sn)
    return retval


  def clear(self):
    for sn in self.synaptons.values():
      sn.clear()


  def check_synaptomes(self, num_rounds):
    """Sets the checked flag on randomly selected synaptons, iff they are fulfilled.
    @param num_rounds: Number of times to pick and check a random synapton.
    """
    entched_sms = list(self.get_entrenched_synaptomes())
    if not len(entched_sms):
      return

    num_rounds = int(num_rounds)
    while num_rounds > 0:
      num_rounds -= 1

      sn = random.choice(entched_sms)

      is_fulfilled = sn.is_fulfilled(self)
      if is_fulfilled != sn.checkstate:
        sn.checkstate = is_fulfilled

      if is_fulfilled and not sn.did_fire:
        sn.did_fire = True


  def receive_reinforcement(self, magnitude):
    for sn in self.synaptons.values():
      sn.receive_reinforcement(magnitude)


  def angst(self):
    """Computes the ratio of fired synaptomes that missed their quotas."""
    pass


  def get_entrenched_synaptomes(self, entrenchment_cutoff_fraction=0, inverse=False):
    """Returns all synaptons whose entrenchment level is nonzero and above the one specified.
    @param entrenchment_cutoff_fraction: Multiply by the max entrenchment of all synaptons, this is a synapton's min required entrenchment.
    @param inverse: If True, returns only *de*entrenched synaptons that *don't* make the cutoff.
    @return: Set of all synaptons above the cutoff.
    """
    if not len(self.synaptons):
      return set()

    if entrenchment_cutoff_fraction > 1 or entrenchment_cutoff_fraction < 0:
      raise ValueError('entrenchment_cutoff_fraction', 'Fraction must be between 0 and 1.')
    max_entch = max([sn.entrenchment for sn in self.synaptons.values()])
    entch_cutoff = entrenchment_cutoff_fraction * max_entch

    entched_sms = []
    if not inverse:
      entched_sms = [sn for sn in self.synaptons.values() if sn.entrenchment > entch_cutoff]
    else:
      entched_sms = [sn for sn in self.synaptons.values() if sn.entrenchment < entch_cutoff]

    return set(entched_sms)



  def get_checked_synaptomes(self, constraint=None, with_command=False):
    """Returns a collection of checked synaptons that meet the specified criteria.
    @param constraint: If set to True or False, returns only synaptons whose checkstate is True or False, respectively.
    @param with_command: If set, returns only synaptons that have a corresponding command.
    @return: Collection of synaptons whose checkstate is not None.
    """
    checked_synaptomes = [sn for sn in self.get_entrenched_synaptomes() if sn.checkstate is not None]
    if constraint is not None:
      checked_synaptomes = [sn for sn in checked_synaptomes if sn.checkstate == constraint]
    if with_command:
      checked_synaptomes = [sn for sn in checked_synaptomes if sn.command is not None]
    checked_synaptomes = list(checked_synaptomes)
    return checked_synaptomes


  def get_linkable_synaptomes(self):
    """Returns all synaptons that are eligible for being used as the dependency for another synapton.
    @return: Set of all linkable synaptons.
    """
    all_sms = set(self.synaptons.values())
    return all_sms


  

  def decay(self, checkstate_decay_prob, entrenchment_decay_prob):
    """Probabilistically clears checkstates and decrements entrenchments and citations.
    NOTE: This could be part of a sleep cycle.
    @param checkstate_decay_prob: The probability for each synapton to get its checkstate cleared.
    @param entrenchment_decay_prob: The probability for each synapton to get its entrenchment decremented.
    @param citation_decay_prob: The probability for each synapton to get its citation count decremented.
    """
    if not len(self.synaptons):
      return

    for sn in self.synaptons.values():
      sn.decay(checkstate_decay_prob, entrenchment_decay_prob)

    # In a separate step, probabilistically delete all deentrenched synaptons.
    # Maybe they were *just* deentrenched, or maybe they had been deentrenched for a
    # while, but either way, they need to be cleaned up.
    # We need to store them off because we can't change dictionary during iteration.
    smkeys_to_delete = set()
    for sn in self.get_entrenched_synaptomes(0, True):
      if True or random.random() < entrenchment_decay_prob:
        smkeys_to_delete.add(sn.name)
    for smkey in smkeys_to_delete:
      del self.synaptons[smkey]

    if not len(self.synaptons):
      raise AssertionError('Should not be able to delete last synapton! Deleted {}'.format(smkeys_to_delete))



  def delete_orphaned_dependencies(self, num_rounds=1):
    """Remove synaptons that are dependent on synaptons that no longer exist.
    TODO: This method is all wrong. A synapton with orphaned dependencies shouldn't
    be deleted. Its missing dependencies should be rerolled.
    NOTE: This could be part of a sleep cycle.
    @param num_rounds: How many times to check all synaptons for dependencies. Any synaptons that 
    are removed in one round may leave other synaptons orphaned and primed for removal in subsequent
    rounds.
    """
    return
    while num_rounds > 0:
      num_rounds -= 1

      smkeys_to_delete = set()
      for smkey, sn in self.synaptons.items():
        depnames = sn.get_named_synaptome_dependencies()
        for depname in depnames:
          if depname not in self.synaptons:
            smkeys_to_delete.add(sn.name)

      for smkey in smkeys_to_delete:
        del self.synaptons[smkey]



  def clear_all_flagged(self):
    """Set the traversal flag on all synaptons to False, to prep for recursive operations."""
    for sn in self.synaptons.values():
      sn.flagged = False


  def delete_sophistries(self):
    """Removes synaptons that aren't dependencies (either direct or indirect) of any action.
    """
    self.clear_all_flagged()
    for sn in self.synaptons.values():
      if sn.is_output():
        sn.recursively_flag_dependencies(self)
    smkeys_to_delete = set()
    for smkey, sn in self.synaptons.items():
      if not sn.flagged:
        smkeys_to_delete.add(smkey)
    for smkey in smkeys_to_delete:
      del self.synaptons[smkey]
    
  # TODO: Delete all synaptons that aren't dependent on any input.


  def choose_command(self, prob_hailmary=0, fn_hailmary=None):
    """Probabilistically chooses a command from the collection of fulfilled synaptons. Automatically sets self.last_command.
    @param prob_hailmary: The probability that we should choose no action at all, and let the game choose for us.
    @param fn_hailmary: A function that randomly generates a command when a hailmary is rolled.
    @return: Command string, or None.
    """
    winner_cmd = None
    is_hailmary = random.random() < prob_hailmary

    if not is_hailmary:
      candidate_sms = self.get_checked_synaptomes(constraint=True, with_command=True)
      if len(candidate_sms):
        # Choose randomly, weighted by the entrenchment of the candidates.
        total_entch = sum([sn.entrenchment for sn in candidate_sms])
        roulette = random.random() * total_entch
        winner_sm = None
        for sn in candidate_sms:
          roulette -= sn.entrenchment
          if roulette <= 0:
            winner_sm = sn
            break
        if not winner_sm:
          raise AssertionError('Your roulette algorithm is broken.')

        winner_cmd = winner_sm.command

    if not winner_cmd and fn_hailmary:
      winner_cmd = fn_hailmary()

    self.last_command = winner_cmd
    return winner_cmd






