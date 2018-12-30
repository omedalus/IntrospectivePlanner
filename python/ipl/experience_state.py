
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
    # The most recent action attempted. 
    # NOTE: This is isomorphic to having a short-term 
    # action memory stack of depth 1.
    self.last_action = None

    # Boolean stating whether or not the precondition 
    # of the last attempted action was satisfied by 
    # the state of the world. 
    # Defaults to False.
    self.was_last_precondition_satisfied = False

    # Boolean to determine if the search can stop. Default is False.
    self.is_victorious = False

    # Rules that represent what the organism believes its next 
    # ExperienceState will be given certain actions (or lacks of
    # action).
    # E.g. "If I advance my pawn, the pawn will be one square
    # ahead of where it currently is."
    self.progression_rules = set()


