import random

# Because this is the baseline maze traverser, all it does is randomly mindlessly bounce
# around, heedless of obstacles or rewards.
def ActionGenerationFunction(frame):
  a = random.choice(['FORWARD', 'TURN_LEFT', 'TURN_RIGHT'])
  return a

# This dumb maze agent doesn't understand consequences.
def ConsequenceGenerationFunction(frame, action):
  return {
    "frame": frame,
    "probability": 1.0,
    "reward": 0
  }



class MazeAgentRandomAction:
  def __init__(self, environment=None):
    self.actionGenerator = ActionGenerationFunction
    self.consequenceGenerator = ConsequenceGenerationFunction
    
    self.environment = environment
    self.currentFrame = None
    
    

  # Perform one full step of reading the sensors, populating or updating the current frame,
  # devising a plan, and acting on that plan.
  def step(self, interactive=False):
    action = self.actionGenerator(self.currentFrame)
    if interactive:
      print(f"Action: {action}")
      
    self.environment.submit_action(action, interactive)
  
  def choose_action(self):
    a = random.choice(['FORWARD', 'TURN_LEFT', 'TURN_RIGHT'])
    return a

  
  
  

  