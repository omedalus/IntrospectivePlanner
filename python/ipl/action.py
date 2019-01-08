
class Action:
  """
  Describes an action that can be taken in a game.
  """

  def __init__(self, command=None, precondition=None):
    # Actions may have preconditions, which have to be 
    # fulfilled in order for the action to be eligible for being taken.
    # The precondition is given as a string specifying a named synapton.
    # TODO: This is dumb. Action should be an affordance of a new synapton.
    self.precondition = precondition

    # The action to take.
    self.command = command

    # NOTE: The action can have game state overrides, which attempt
    # to describe how the game state will have changed as a result of
    # taking the action. Actually, this should probably be an
    # evolvable collection.


  def __repr__(self):
    prestr = '(T)' if not self.precondition else str(self.precondition)
    retval = prestr + '=>' + self.command
    return retval

