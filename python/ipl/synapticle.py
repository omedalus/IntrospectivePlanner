



class Synapticle:
  """
  A criterion that describes a condition of the experience state
  that must be met in order for a Synapton to activate.
  """
  BASES = set(['INPUT', 'CHECKED', 'REGISTER', 'LAST_ACTION'])

  def __init__(self, basis, key, value):
    if basis is None:
      raise ValueError('basis', 'Basis must be specified.')

    if basis not in Synapticle.BASES:
      raise ValueError('basis', 'Unknown basis: ' + str(basis))

    if basis == 'INPUT':
      if key is None:
        raise ValueError('key', 'Key must be specified for INPUT basis.')
      if value is not True:
        raise ValueError('value', 'Value must be True for INPUT basis.')
    elif basis == 'CHECKED':
      if key is None:
        raise ValueError('key', 'Key must be specified for CHECKED basis.') 
    elif basis == 'LAST_ACTION':
      raise NotImplementedError('LAST_ACTION not implemented yet')
    elif basis == 'REGISTER':
      raise NotImplementedError('REGISTER basis not yet supported')

    self.basis = basis
    self.key = key
    self.value = value

  def is_fulfilled(self, experience_state):
    if self.basis == 'INPUT':
      return (self.key in experience_state.inputs) == self.value
    elif self.basis == 'CHECKED':
      s = experience_state.synaptons.get(self.key)
      chst = s.checkstate if s else None
      return chst == self.value
    elif self.basis == 'LAST_ACTION':
      return experience_state.last_command == self.value
    elif self.basis == 'REGISTER':
      raise AssertionError('REGISTER basis not yet supported')

  def __repr__(self):
    retval = ''
    if self.basis == 'INPUT':
      retval += 'INPUT:' + ('' if self.value else '!') + self.key
    elif self.basis == 'CHECKED' or self.basis == 'INPUT':
      if self.value is None:
        retval += '!'
      retval += 'CHECKED:'
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


