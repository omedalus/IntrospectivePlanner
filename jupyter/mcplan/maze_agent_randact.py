import random

class MazeAgentRandomAction:

  def __init__(self, environment=None):
    self.environment = environment

  # Perform one full step of reading the sensors, populating or updating the current frame,
  # devising a plan, and acting on that plan.
  def step(self, interactive=False):
    a = self.choose_action()
    self.environment.submit_action(a, interactive)
  
  # Because this is the baseline maze traverser, all it does is randomly mindlessly bounce
  # around, heedless of obstacles or rewards.
  def choose_action(self):
    a = random.choice(['FORWARD', 'TURN_LEFT', 'TURN_RIGHT'])
    return a

  
  
  
  
  