class Action:
  """
  Describes an action that can be taken in a game.
  """

  def __init__(self):
    # Actions may have preconditions, which have to be 
    # fulfilled in order for the action to be taken.
    self.precondition = None

    # The action to take.
    self.action = None
