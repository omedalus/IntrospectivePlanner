



class Synapton:
  """
  A criterion that describes a condition of the experience state
  that must be met in order for a Synaptome to activate.
  """
  BASES = set(['GAME', 'CHECKED', 'LAST_ACTION', 'REGISTERS'])

  def __init__(self, basis, key=None, value=None):
    # If basis is GAME or CHECKED, then the key must be specified; 
    # if the value isn't specified then it defaults to True.
    # If the basis is LAST_ACTION, then the value must be specified;
    # if the key is specified instead, then it's presumed to be the
    # value.

    if basis is None:
      raise ValueError('basis', 'Basis must be specified.')

    if basis not in Synapton.BASES:
      raise ValueError('basis', 'Unknown basis: ' + str(basis))

    if basis == 'CHECKED' or basis == 'GAME':
      if key is None:
        raise ValueError('key', 'Key must be specified for CHECKED basis.') 
      if value is None:
        value = True
    elif basis == 'LAST_ACTION':
      if key:
        if value is not None:
          raise ValueError('key', 'Cannot specify both key and value for LAST_ACTION basis.')
        else:
          value = key
          key = None
    elif basis == 'REGISTERS':
      raise NotImplementedError('REGISTERS basis not yet supported')

    self.basis = basis
    self.key = key
    self.value = value

  def is_fulfilled(self, experience_state, game_state):
    if self.basis == 'GAME':
      return self.key in game_state
    elif self.basis == 'CHECKED':
      if self.key not in experience_state.checked:
        return False
      return experience_state.checked[self.key] == self.value
    elif self.basis == 'LAST_ACTION':
      return experience_state.last_command == self.value

  def __repr__(self):
    retval = self.basis + ':'
    if self.basis == 'CHECKED' or self.basis == 'GAME':
      if self.value == False:
        retval += '!'
      retval += self.key
    elif self.basis == 'LAST_ACTION':
      retval += self.value
    return retval

  def __eq__(self, other):
    if self.basis != other.basis:
      return False
    if self.key != other.key:
      return False
    if self.value != other.value:
      return False
    return True

  def __hash__(self):
    retstr = ''
    retstr += str(len(self.basis))
    retstr += '_'
    retstr += self.basis
    if self.key is None:
      retstr += 'X'
    else:
      retstr += str(len(self.key))
      retstr += '_'
      retstr += self.key
    if self.value is None:
      retstr += 'X'
    else:
      retstr += str(len(self.value) if isinstance(self.value, str) else 0)
      retstr += '_'
      retstr += str(self.value)
    return hash(retstr)


