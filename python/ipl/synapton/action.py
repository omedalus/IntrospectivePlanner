
class Action:
  """
  Describes an action that can be taken in a game.
  """

  def __init__(self, basis, key, value):
    self.basis = basis
    self.key = key
    self.value = value


  def __repr__(self):
    retval = '{}:{}{}'.format(
      self.basis,
      '' if self.value else '!',
      self.key
    )
    return retval

