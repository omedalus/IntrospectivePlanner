
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
    for sm in [sm for sm in self.synaptomes.values() if sm in self.get_entrenched_synaptomes()]:
      retval += '\t\t{}\n'.format(sm)
    for sm in [sm for sm in self.synaptomes.values() if sm not in self.get_entrenched_synaptomes()]:
      retval += '\t\t{}\n'.format(sm)
    return retval


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
        is_fulfilled = sm.is_fulfilled(self, game_state)
        if is_fulfilled != sm.checkstate:
          sm.checkstate = is_fulfilled


  def get_entrenched_synaptomes(self, entrenchment_cutoff_fraction=.5, inverse=False):
    """Returns all synaptomes whose entrenchment level is nonzero and above the one specified.
    @param entrenchment_cutoff_fraction: Multiply by the max entrenchment of all synaptomes, this is a synaptome's min required entrenchment.
    @param inverse: If True, returns only *de*entrenched synaptomes that *don't* make the cutoff.
    @return: Set of all synaptomes above the cutoff.
    """
    if entrenchment_cutoff_fraction > 1 or entrenchment_cutoff_fraction < 0:
      raise ValueError('entrenchment_cutoff_fraction', 'Fraction must be between 0 and 1.')
    max_entch = max([sm.entrenchment for sm in self.synaptomes.values()])
    entch_cutoff = entrenchment_cutoff_fraction * max_entch

    entched_sms = []
    if not inverse:
      entched_sms = [sm for sm in self.synaptomes.values() if sm.entrenchment > entch_cutoff]
    else:
      entched_sms = [sm for sm in self.synaptomes.values() if sm.entrenchment <= entch_cutoff]
      
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
    @param checkstate_decay_prob: The probability for each synaptome to get its checkstate cleared.
    @param entrenchment_decay_prob: The probability for each synaptome to get its entrenchment decremented.
    @param citation_decay_prob: The probability for each synaptome to get its citation count decremented.
    """
    for sm in self.synaptomes.values():
      sm.decay(checkstate_decay_prob, entrenchment_decay_prob)

    # In a separate step, probabilistically delete all deentrenched synaptomes.
    # Maybe they were *just* deentrenched, or maybe they had been deentrenched for a
    # while, but either way, they need to be cleaned up.
    # We need to store them off because we can't change dictionary during iteration.
    smkeys_to_delete = set()
    for sm in self.get_entrenched_synaptomes(entrenchment_decay_prob, True):
      if random.random() < entrenchment_decay_prob:
        smkeys_to_delete.add(sm.name)
    for smkey in smkeys_to_delete:
      del self.synaptomes[smkey]



  def choose_command(self, prob_hailmary=0, fn_hailmary=None):
    """Probabilistically chooses a command from the collection of fulfilled synaptomes. Automatically sets self.last_command.
    @param prob_hailmary: The probability that we should choose no action at all, and let the game choose for us.
    @param fn_hailmary: A function that randomly generates a command when a hailmary is rolled.
    @return: Command string, or None.
    """
    # NOTE: Maybe the hailmary prob rises as time goes on and no reward is found? Maybe that's what frustration is all about?
    # NOTE: We can turn this into a GA eventually, possibly, if we have to.
    winner_cmd = None
    is_hailmary = random.random() < prob_hailmary

    if not is_hailmary:
      candidate_sms = self.get_checked_synaptomes(constraint=True, with_command=True)
      if len(candidate_sms):
        winner_sm = random.sample(candidate_sms, 1)[0]
        winner_cmd = winner_sm.command

    if not winner_cmd and fn_hailmary:
      winner_cmd = fn_hailmary()

    self.last_command = winner_cmd
    return winner_cmd






