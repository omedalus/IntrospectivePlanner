import ipl 
import pickle


results = []

for itrial in range(100):
  trialresults = []

  game = ipl.games.ElMazeGame(3,2)

  organism = ipl.Organism()
  organism.configure(game.player_config())

  organism.reset_state()

  for irun in range(20):
    print('Trial {:4d}\tRun {:4d}'.format(itrial+1, irun+1))

    game = ipl.games.ElMazeGame(3,2)
    organism.reset_state()
    
    while not game.eof():
      organism.handle_sensor_input(game.sensors())
      oa = organism.choose_action()
      game.act(oa.actuators)

      if game.turn % 100 == 0:
        print('\tTurns elapsed: {:4d}\tExperience repo size: {:8d}'.format(game.turn, len(organism.experience_repo) ))


    organism.handle_sensor_input(game.sensors())
    organism.maintenance()

    print('\tCompleted in {:4d} turns.'.format(game.turn))
    print()

    trialresults.append(game.turn)
  results.append(trialresults)

print(results)



