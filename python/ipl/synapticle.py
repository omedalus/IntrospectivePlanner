



class Synapticle:
  """
  A criterion that describes a condition of the experience state
  that must be met in order for a Synapton to activate.
  """
  BASES = set(['INPUT', 'CHECKED', 'REGISTER', 'LAST_ACTION'])

  def __init__(self, basis, key=None, value=None):
    # If basis is GAME or CHECKED, then the key must be specified; 
    # if the value isn't specified then it defaults to True.
    # If the basis is LAST_ACTION, then the value must be specified;
    # if the key is specified instead, then it's presumed to be the
    # value.

    if basis is None:
      raise ValueError('basis', 'Basis must be specified.')

    if basis not in Synapticle.BASES:
      raise ValueError('basis', 'Unknown basis: ' + str(basis))

    if basis == 'INPUT':
      if key is None:
        raise ValueError('key', 'Key must be specified for INPUT basis.') 
      if value is None:
        value = True
      if value is not True:
        raise ValueError('value', 'Value is assumed to be True for INPUT basis.')
      value = True
    elif basis == 'CHECKED':
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
    elif basis == 'REGISTER':
      raise NotImplementedError('REGISTER basis not yet supported')

    self.basis = basis
    self.key = key
    self.value = value

  def is_fulfilled(self, experience_state):
    if self.basis == 'INPUT':
      return self.key in experience_state.inputs
    elif self.basis == 'CHECKED':
      s = experience_state.synaptons.get(self.key)
      if not s or s.checkstate is None:
        return False
      return s.checkstate == self.value
    elif self.basis == 'LAST_ACTION':
      return experience_state.last_command == self.value
    elif self.basis == 'REGISTER':
      raise AssertionError('REGISTER basis not yet supported')

  def __repr__(self):
    retval = self.basis + ':'
    if self.basis == 'CHECKED' or self.basis == 'INPUT':
      if self.value == False:
        retval += '!'
      retval += self.key
    elif self.basis == 'LAST_ACTION':
      retval += self.value
    elif self.basis == 'REGISTER':
      raise AssertionError('REGISTER basis not yet supported')
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


