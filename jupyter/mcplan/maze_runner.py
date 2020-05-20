#!/usr/bin/python3

from maze_environment import MazeEnvironment
from maze_agent_randact import MazeAgentRandomAction

environment = MazeEnvironment(filename="L-map.txt")
agent = MazeAgentRandomAction(environment)

environment.show()

numStep = 0
while True:
  numStep += 1
  print('')
  print(f"Step {numStep}")

  agent.step(True)

  if environment.reward() > 0:
    break
  
  