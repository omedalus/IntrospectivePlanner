
import random

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
    for s in self.synaptomes.values():
      retval += '\t\t{}\n'.format(s)
    return retval


  def check_synaptomes(self, game_state, num_checks_per_round, num_rounds):
    """Sets the checked flag on randomly selected synaptomes.
    @param game_state: A set of atoms that are true in the world.
    @param num_checks_per_round: How many synaptomes to check in each round.
    @param num_rounds: Maximum number of rounds to check.
    """
    num_rounds = int(num_rounds)
    while num_rounds > 0:
      num_rounds -= 1
      is_dirty = False

      sm_to_test = []
      if len(self.synaptomes) <= num_checks_per_round:
        sm_to_test = self.synaptomes.values()
      else:
        sm_to_test = random.sample(set(self.synaptomes.values()), num_checks_per_round)

      for sm in sm_to_test:
        is_fulfilled = sm.is_fulfilled(self, game_state)
        if is_fulfilled != sm.checkstate:
          is_dirty = True
          sm.checkstate = is_fulfilled
      if not is_dirty:
        break



  def get_checked_synaptomes(self, constraint=None, with_command=False):
    """Returns a collection of checked synaptomes that meet the specified criteria.
    @param constraint: If set to True or False, returns only synaptomes whose checkstate is True or False, respectively.
    @param with_command: If set, returns only synaptomes that have a corresponding command.
    @return: Collection of synaptomes whose checkstate is not None.
    """
    checked_synaptomes = [sm for sm in self.synaptomes.values() if sm.checkstate is not None]
    if constraint is not None:
      checked_synaptomes = [sm for sm in checked_synaptomes if sm.checkstate == constraint]
    if with_command:
      checked_synaptomes = [sm for sm in checked_synaptomes if sm.command is not None]
    return list(checked_synaptomes)

  

  def clear_checkstates(self, clear_probability = 1):
    """Probabilistically clears the checkstates of currently checked synaptomes, setting them to None.
    @param clear_probability: The probability for each synaptome to get its checkstate cleared.
    """
    for sm in self.get_checked_synaptomes():
      if clear_probability != 1 and random.random() > clear_probability:
        continue
      sm.checkstate = None


  def choose_command(self, prob_hailmary=0):
    """Probabilistically chooses a command from the collection of fulfilled synaptomes.
    @param prob_hailmary: The probability that we should choose no action at all, and let the game choose for us.
    @return: Command string, or None.
    """
    # NOTE: Maybe the hailmary prob rises as time goes on and no reward is found? Maybe that's what frustration is all about?
    # NOTE: We can turn this into a GA eventually, possibly, if we have to.
    if random.random() < prob_hailmary:
      return None
    candidate_sms = self.get_checked_synaptomes(constraint=True, with_command=True)
    if not len(candidate_sms):
      return None
    winner_sm = random.sample(candidate_sms, 1)[0]
    return winner_sm.command






