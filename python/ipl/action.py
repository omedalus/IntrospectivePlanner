
class Action:
  """
  Describes an action that can be taken in a game.
  """

  def __init__(self, command=None, precondition=None):
    # Actions may have preconditions, which have to be 
    # fulfilled in order for the action to be eligible for being taken.
    # The precondition is given as a named synaptome.
    self.precondition = precondition

    # The action to take.
    self.command = command

  def __str__(self):
    synaptomestr = '(T)' if not self.synaptome else str(self.synaptome)
    retval = synaptomestr + '=>' + self.command
    return retval

