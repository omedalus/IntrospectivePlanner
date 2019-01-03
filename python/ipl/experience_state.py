
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


  def get_checked_synaptomes(self, constraint=None, with_command=False):
    checked_synaptomes = [s for s in self.synaptomes.values() if s.checkstate is not None]
    if constraint is not None:
      checked_synaptomes = [s for s in checked_synaptomes if s.checkstate == constraint]
    if with_command:
      checked_synaptomes = [s for s in checked_synaptomes if s.command is not None]
    return list(checked_synaptomes)

  
  def clear_checkstates(self, clear_probability = 1):
    for s in self.synaptomes.values():
      if clear_probability != 1 and random.random() > clear_probability:
        continue
      s.checkstate = None





