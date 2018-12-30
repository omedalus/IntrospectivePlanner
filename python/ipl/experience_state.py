
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
    # Rules that represent which actions can be taken under
    # which circumstances.
    self.action_rules = set()

    # A map of recently checked values. These can be sensor inputs,
    # internal registers, stencils, etc. They're specified by
    # string, and mapped to a Boolean.
    self.checked = {}

