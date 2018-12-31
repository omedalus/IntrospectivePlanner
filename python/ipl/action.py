
class Action:
  """
  Describes an action that can be taken in a game.
  """

  def __init__(self, command=None, synaptome=None):
    # Actions may have preconditions, which have to be 
    # fulfilled in order for the action to be taken.
    self.synaptome = synaptome

    # The action to take.
    self.command = command

  def __str__(self):
    synaptomestr = '(T)' if not self.synaptome else str(self.synaptome)
    retval = synaptomestr + '=>' + self.command
    return retval

