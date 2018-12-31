class Action:
  """
  Describes an action that can be taken in a game.
  """

  def __init__(self, command=None, precondition=None):
    # Actions may have preconditions, which have to be 
    # fulfilled in order for the action to be taken.
    self.precondition = precondition

    # The action to take.
    self.command = command

  def __str__(self):
    preconditionstr = '(T)' if not self.precondition else str(self.precondition)
    retval = preconditionstr + '=>' + self.command
    return retval

