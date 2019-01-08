
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
    
    # A count of how long this organism has been alive.
    self.turncount = 0


  def __repr__(self):
    retval = '\tLast command: {}\n'.format(self.last_command)
    retval += '\tSynaptomes:\n'

    sms = list([sn for sn in self.synaptons.values()])
    sms.sort(key = lambda sn: -sn.expectation.mean())

    for sn in sms:
      retval += '\t\t{}\n'.format(sn)
    return retval


  def clear(self):
    for sn in self.synaptons.values():
      sn.clear()


  def check_synaptons(self, num_rounds):
    """Sets the checked flag on randomly selected synaptons, iff they are fulfilled.
    @param num_rounds: Number of times to pick and check a random synapton.
    """
    sns = list(self.synaptons.values())
    sns = [sn for sn in sns if not sn.is_tentative]
    if not len(sns):
      return

    num_rounds = int(num_rounds)
    while num_rounds > 0:
      num_rounds -= 1

      sn = random.choice(sns)

      is_fulfilled = sn.is_fulfilled(self)
      if is_fulfilled != sn.checkstate:
        sn.checkstate = is_fulfilled

      if is_fulfilled and not sn.did_fire:
        sn.did_fire = True


  def receive_reinforcement(self, magnitude):
    for sn in self.synaptons.values():
      sn.receive_reinforcement(magnitude)


  
  def start_turn(self):
    self.turncount += 1
    for sn in self.synaptons.values():
      #sn.is_tentative = False
      pass


  def angst(self):
    """Computes the fraction of fired synaptomes that missed their quotas.
    @return: float between 0 and 1.
    """
    sns_fired = [sn for sn in self.synaptons.values() if sn.did_fire]
    sns_missed_quota = [sn for sn in sns_fired if not sn.did_make_quota]

    if not len(sns_fired):
      return 0

    retval = len(sns_missed_quota) / len(sns_fired)
    return retval



  def get_checked_synaptons(self, constraint=None, with_command=False):
    """Returns a collection of checked synaptons that meet the specified criteria.
    @param constraint: If set to True or False, returns only synaptons whose checkstate is True or False, respectively.
    @param with_command: If set, returns only synaptons that have a corresponding command.
    @return: Collection of synaptons whose checkstate is not None.
    """
    checked_sns = [sn for sn in self.synaptons.values() if sn.checkstate is not None]
    if constraint is not None:
      checked_sns = [sn for sn in checked_sns if sn.checkstate == constraint]
    if with_command:
      checked_sns = [sn for sn in checked_sns if sn.command is not None]
    checked_sns = list(checked_sns)
    return checked_sns


  def get_linkable_synaptons(self):
    """Returns all synaptons that are eligible for being used as the dependency for another synapton.
    @return: Set of all linkable synaptons.
    """
    all_sms = set(self.synaptons.values())
    return all_sms





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


  def generate_random_synaptom(self):
    """Create a random synapton and add it to our set."""
    randname = 'SN_' + str(int(random.random() * 1000000000))



  def choose_command(self, prob_hailmary=0, fn_hailmary=None):
    """Probabilistically chooses a command from the collection of fulfilled synaptons. Automatically sets self.last_command.
    @param prob_hailmary: The probability that we should choose no action at all, and let the game choose for us.
    @param fn_hailmary: A function that randomly generates a command when a hailmary is rolled.
    @return: Command string, or None.
    """
    winner_cmd = None
    is_hailmary = random.random() < prob_hailmary

    if not is_hailmary:
      candidate_sns = self.get_checked_synaptons(constraint=True, with_command=True)
      if len(candidate_sns):
        winner_sn = random.choice(candidate_sns)
        winner_cmd = winner_sn.command

    if not winner_cmd and fn_hailmary:
      winner_cmd = fn_hailmary()

    self.last_command = winner_cmd
    return winner_cmd






