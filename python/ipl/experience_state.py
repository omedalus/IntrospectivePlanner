
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
    # Inputs received from the organism's external sensors,
    # reflecting the state of the outside world.
    # E.g. sound, light, odor, etc.
    self.external_inputs = set()

    # Inputs received from sensors inside the organism's body,
    # reflecting the state of the organism's makeup.
    # E.g. "I'm hungry", "I'm hot", or even explicit mental 
    # modes such as "I'm angry."
    self.somatic_inputs = set()

    # Working memory notes that the organism has made for itself.
    # E.g. "I'm working on a knight's gambit right now."
    self.registers = set()

    # Rules that represent how satisfying it believes this state 
    # will be, in and of its own right.
    # E.g. "When I am in a checkmate, I am unhappy."
    self.evaluation_rules = set()

    # Rules that represent what the organism believes its next 
    # ExperienceState will be given certain actions (or lacks of
    # action).
    # E.g. "If I advance my pawn, the pawn will be one square
    # ahead of where it currently is."
    self.progression_rules = set()
