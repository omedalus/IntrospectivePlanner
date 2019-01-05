
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

    # A map of named synaptomes. Synaptomes get checked against
    # an existing experience state, so checking them is a free action.
    # NOTE: Maybe the organism can choose to check a named synaptome,
    # or maybe checking synaptomes is itself an action.
    self.synaptomes = {}
    

  def __repr__(self):
    retval = '\tLast command: {}\n'.format(self.last_command)
    retval += '\tSynaptomes:\n'

    sms = list([sm for sm in self.synaptomes.values()])
    sms.sort(key = lambda sm: -sm.entrenchment)

    for sm in sms:
      retval += '\t\t{}\n'.format(sm)
    return retval


  def clear(self):
    for sm in self.synaptomes.values():
      sm.clear()


  def check_synaptomes(self, game_state, num_checks_per_round, num_rounds):
    """Sets the checked flag on randomly selected synaptomes. Only checks entrenched synaptomes.
    @param game_state: A set of atoms that are true in the world.
    @param num_checks_per_round: How many synaptomes to check in each round.
    @param num_rounds: Maximum number of rounds to check.
    """
    entched_sms = list(self.get_entrenched_synaptomes())
    if not len(entched_sms):
      return

    num_rounds = int(num_rounds)
    while num_rounds > 0:
      num_rounds -= 1
      # NOTE: We used to check a dirty flag here, and shortcut
      # the rounds if nothing was changed this round. Turns out
      # that's not a great thing to do, because we didn't necessarily
      # sample all synaptomes in this round (we in fact probably didn't),
      # so we should perform more rounds because subsequent rounds
      # will pick up synaptomes with changes that we didn't catch
      # in this round.

      random.shuffle(entched_sms)
      sm_to_test = entched_sms[:num_checks_per_round]

      for sm in sm_to_test:
        sm.increment_checkcount(1, recursion_depth=1, experience_state=self)
        is_fulfilled = sm.is_fulfilled(self, game_state)
        if is_fulfilled != sm.checkstate:
          sm.checkstate = is_fulfilled
        
        if sm.inhibit is not None:
          sminh = self.synaptomes.get(sm.inhibit)
          if sminh:
            sminh.checkstate = None


  def get_entrenched_synaptomes(self, entrenchment_cutoff_fraction=0, inverse=False):
    """Returns all synaptomes whose entrenchment level is nonzero and above the one specified.
    @param entrenchment_cutoff_fraction: Multiply by the max entrenchment of all synaptomes, this is a synaptome's min required entrenchment.
    @param inverse: If True, returns only *de*entrenched synaptomes that *don't* make the cutoff.
    @return: Set of all synaptomes above the cutoff.
    """
    if not len(self.synaptomes):
      return set()

    if entrenchment_cutoff_fraction > 1 or entrenchment_cutoff_fraction < 0:
      raise ValueError('entrenchment_cutoff_fraction', 'Fraction must be between 0 and 1.')
    max_entch = max([sm.entrenchment for sm in self.synaptomes.values()])
    entch_cutoff = entrenchment_cutoff_fraction * max_entch

    entched_sms = []
    if not inverse:
      entched_sms = [sm for sm in self.synaptomes.values() if sm.entrenchment > entch_cutoff]
    else:
      entched_sms = [sm for sm in self.synaptomes.values() if sm.entrenchment < entch_cutoff]

    return set(entched_sms)



  def get_checked_synaptomes(self, constraint=None, with_command=False):
    """Returns a collection of checked synaptomes that meet the specified criteria.
    @param constraint: If set to True or False, returns only synaptomes whose checkstate is True or False, respectively.
    @param with_command: If set, returns only synaptomes that have a corresponding command.
    @return: Collection of synaptomes whose checkstate is not None.
    """
    checked_synaptomes = [sm for sm in self.get_entrenched_synaptomes() if sm.checkstate is not None]
    if constraint is not None:
      checked_synaptomes = [sm for sm in checked_synaptomes if sm.checkstate == constraint]
    if with_command:
      checked_synaptomes = [sm for sm in checked_synaptomes if sm.command is not None]
    checked_synaptomes = list(checked_synaptomes)
    return checked_synaptomes

  

  def decay(self, checkstate_decay_prob, entrenchment_decay_prob):
    """Probabilistically clears checkstates and decrements entrenchments and citations.
    NOTE: This could be part of a sleep cycle.
    @param checkstate_decay_prob: The probability for each synaptome to get its checkstate cleared.
    @param entrenchment_decay_prob: The probability for each synaptome to get its entrenchment decremented.
    @param citation_decay_prob: The probability for each synaptome to get its citation count decremented.
    """
    if not len(self.synaptomes):
      return

    for sm in self.synaptomes.values():
      sm.decay(checkstate_decay_prob, entrenchment_decay_prob)

    # In a separate step, probabilistically delete all deentrenched synaptomes.
    # Maybe they were *just* deentrenched, or maybe they had been deentrenched for a
    # while, but either way, they need to be cleaned up.
    # We need to store them off because we can't change dictionary during iteration.
    smkeys_to_delete = set()
    for sm in self.get_entrenched_synaptomes(.25, True):
      if random.random() < 1:
        smkeys_to_delete.add(sm.name)
    for smkey in smkeys_to_delete:
      del self.synaptomes[smkey]

    if not len(self.synaptomes):
      raise AssertionError('Should not be able to delete last synaptome! Deleted {}'.format(smkeys_to_delete))



  def delete_orphaned_dependencies(self, num_rounds=1):
    """Remove synaptomes that are dependent on synaptomes that no longer exist.
    NOTE: This could be part of a sleep cycle.
    @param num_rounds: How many times to check all synaptomes for dependencies. Any synaptomes that 
    are removed in one round may leave other synaptomes orphaned and primed for removal in subsequent
    rounds.
    """
    while num_rounds > 0:
      num_rounds -= 1

      smkeys_to_delete = set()
      for smkey, sm in self.synaptomes.items():
        depnames = sm.get_named_synaptome_dependencies()
        for depname in depnames:
          if depname not in self.synaptomes:
            smkeys_to_delete.add(sm.name)

      for smkey in smkeys_to_delete:
        del self.synaptomes[smkey]

      # Clean up orphaned inhibitors.
      # I guess this inhibitor won the battle.
      for sm in self.synaptomes.values():
        if not sm.inhibit:
          continue
        if sm.inhibit not in self.synaptomes:
          sm.inhibit = None



  def clear_all_flagged(self):
    """Set the traversal flag on all synaptomes to False, to prep for recursive operations."""
    for sm in self.synaptomes.values():
      sm.flagged = False


  def delete_sophistries(self):
    """Removes synaptomes that aren't dependencies (either direct or indirect) of any action.
    """
    self.clear_all_flagged()
    for sm in self.synaptomes.values():
      if sm.is_output():
        sm.recursively_flag_dependencies(self)
    smkeys_to_delete = set()
    for smkey, sm in self.synaptomes.items():
      if not sm.flagged:
        smkeys_to_delete.add(smkey)
    for smkey in smkeys_to_delete:
      del self.synaptomes[smkey]
    
  # TODO: Delete all synaptomes that aren't dependent on any input.


  def choose_command(self, prob_hailmary=0, fn_hailmary=None):
    """Probabilistically chooses a command from the collection of fulfilled synaptomes. Automatically sets self.last_command.
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
        total_entch = sum([sm.entrenchment for sm in candidate_sms])
        roulette = random.random() * total_entch
        winner_sm = None
        for sm in candidate_sms:
          roulette -= sm.entrenchment
          if roulette <= 0:
            winner_sm = sm
            break
        if not winner_sm:
          raise AssertionError('Your roulette algorithm is broken.')

        winner_cmd = winner_sm.command

        # Not so fast. Now that we've chosen our winner command, let's consolidate
        # the reward. We do this so as to encourage parsimony in the synaptome regime;
        # otherwise we have dozens of synaptomes all clamouring for the opportunity
        # to announce the same action.
        # Find the most active guy who was advocating this action, and give him
        # all the credit.
        sms_with_winner_cmd = [sm for sm in candidate_sms if sm.command == winner_cmd]
        max_chkct_with_winner_cmd = max([sm.checkcount for sm in sms_with_winner_cmd])
        winner_sm = [sm for sm in candidate_sms if sm.checkcount == max_chkct_with_winner_cmd][0]
        winner_sm.increment_checkcount(1, recursion_depth=1, experience_state=self)


    if not winner_cmd and fn_hailmary:
      winner_cmd = fn_hailmary()

    self.last_command = winner_cmd
    return winner_cmd






