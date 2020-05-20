
class MazeEnvironment:

  def __init__(self, mapstring=None, filename=None):
    self.agentPosition = [0, 0]
    self.agentOrientation = 0
    self.goalPosition = [0, 0]
    
    # Each square of the map is an integer that describes traversibility.
    # False = nontraversible
    # True = traversible
    # NOTE: Map is stored as [y][x]
    self.mapDimensions = [0, 0]
    self.map = [[]]
    if mapstring:
      self.load_map_from_string(mapstring)
    elif filename:
      self.load_map_from_file(filename)
      
  
  def load_map_from_file(self, filename):
    with open(filename) as f:
      s = f.read()
      self.load_map_from_string(s)
  
  def load_map_from_string(self, mapstring):
    maprowchars = [list(rowstr) for rowstr in mapstring.split('\n') if len(rowstr) > 0]
    
    longestrowlen = max([len(row) for row in maprowchars])
    self.map = []
    
    for iRow, row in enumerate(maprowchars):
      self.map.append([False] * longestrowlen)
      for iCh, ch in enumerate(row):
        if maprowchars[iRow][iCh] != '#':
          self.map[iRow][iCh] = True
        if maprowchars[iRow][iCh] == 'S':
          self.agentPosition = [iCh, iRow]
        if maprowchars[iRow][iCh] == '*':
          self.goalPosition = [iCh, iRow]
    
    self.mapDimensions = [longestrowlen, len(self.map)]
  
  
  def agentmapsquare(self):
    sq = self.mapsquare(self.agentPosition, self.agentOrientation)
    return sq
    
    
  def is_valid_coord(self, xy):
    if any([d < 0 for d in xy]):
      return False
    if any([d >= self.mapDimensions[iD] for iD, d in enumerate(xy)]):
      return False
    return True
    
    
  def get_relative_ahead_xy(self, xy, orientation):
    from operator import add
    viewmods = [[0,-1], [1,0], [0,1], [-1,0]]
    viewmod = viewmods[orientation]
    viewxy = list(map(add, xy, viewmod))
    return viewxy
  
  
  def mapsquare(self, xy, orientation=0):
    x = xy[0]
    y = xy[1]
    outdict = {
      "traversible": self.map[y][x],
      "goal": xy == self.goalPosition,
      "agent": xy == self.agentPosition,
      "view": [False]*4
    }
    
    # Build a view in order of: Ahead, Left, Right, Behind.
    # First build the view assuming facing North, then rotate as needed.
    from operator import add
    for iDirection in range(4):
      viewxy = self.get_relative_ahead_xy(xy, iDirection)
      if not self.is_valid_coord(viewxy):
        continue
      if self.map[viewxy[1]][viewxy[0]]:
        outdict["view"][iDirection] = True
    
    # Rotate the view array to correspond to the orientation.
    if orientation != 0:
      outdict["view"] = outdict["view"][orientation:] + outdict["view"][:orientation]
    
    return outdict
    
  
  
  def show(self):
    for y in range(self.mapDimensions[1]):
      for x in range(self.mapDimensions[0]):
        sq = self.mapsquare([x, y])
        
        ch = '*' if sq["goal"] else ' ' if sq["traversible"] else '#'
        if sq["agent"]:
          ch = list("^>v<")[self.agentOrientation]

        print(ch, end='')
      print("")
    
    sq = self.agentmapsquare()
    print("Agent sees openings: ")
    if sq["view"][0]:
      print("AHEAD")
    if sq["view"][1]:
      print("RIGHT")
    if sq["view"][2]:
      print("BEHIND")
    if sq["view"][3]:
      print("LEFT")
    
  
  
  def submit_action(self, action, interactive=False):
    if action == "TURN_LEFT":
      self.agentOrientation = (self.agentOrientation + 3) % 4
    elif action == "TURN_RIGHT":
      self.agentOrientation = (self.agentOrientation + 1) % 4
    elif action == "FORWARD":
      toxy = self.get_relative_ahead_xy(self.agentPosition, self.agentOrientation)
      tosq = self.mapsquare(toxy)
      if tosq["traversible"]:
        self.agentPosition = toxy
      
    if interactive:
      self.show()
      
  
  def read_sensors(self):
    sq = self.agentmapsquare()
    return sq["view"]
  
    
  def reward(self):
    if self.agentPosition == self.goalPosition:
      return 100
    return 0
  
  
  
  