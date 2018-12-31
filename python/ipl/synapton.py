



class Synapton:
  """
  A criterion that describes a condition of the experience state
  that must be met in order for a Synaptome to activate.
  """
  BASES = set(['CHECKED', 'LAST_ACTION', 'REGISTERS'])

  def __init__(self, basis, key=None, value=None):
    # If basis is CHECKED, then the key must be specified; if the value
    # isn't specified then it defaults to True.
    # If the basis is LAST_ACTION, then the value must be specified;
    # if the key is specified instead, then it's presumed to be the
    # value.

    if not basis:
      raise ValueError('basis', 'Basis must be specified.')

    if basis not in Synapton.BASES:
      raise ValueError('basis', 'Unknown basis: ' + str(basis))

    if basis == 'CHECKED':
      if not key:
        raise ValueError('key', 'Key must be specified for CHECKED basis.') 
      if not value:
        value = True
    elif basis == 'LAST_ACTION':
      if key:
        if value:
          raise ValueError('key', 'Cannot specify both key and value for LAST_ACTION basis.')
        else:
          value = key
          key = None
    elif basis == 'REGISTERS':
      raise NotImplementedError('REGISTERS basis not yet supported')

    self.basis = basis
    self.key = key
    self.value = value

  def is_fulfilled(self, experience_state):
    if self.basis == 'CHECKED':
      if self.key not in experience_state.checked:
        return False
      return experience_state.checked[self.key] == self.value
    elif self.basis == 'LAST_ACTION':
      return experience_state.last_command == self.value

  def __str__(self):
    retval = self.basis + ':'
    if self.basis == 'CHECKED':
      if not self.value:
        retval += '!'
      retval += self.key
    elif self.basis == 'LAST_ACTION':
      retval += self.value
    return retval

