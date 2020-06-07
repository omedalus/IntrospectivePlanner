import ipl 
import pickle
import random


results = []

for itrial in range(100):
  trialresults = []

  game = ipl.games.ElMazeGame(3,2)

  organism = ipl.Organism()
  organism.configure(game.player_config())

  organism.reset_state()

  for irun in range(20):
    print('Trial {:4d}\tRun {:4d}'.format(itrial+1, irun+1))


    game = ipl.games.ElMazeGame(random.randint(1,20), random.randint(1,20))
    print(game.title)
    organism.reset_state()
    
    while not game.eof():
      organism.handle_sensor_input(game.sensors())
      oa = organism.choose_action()
      game.act(oa.actuators)

      print('\tTrial {:4d}\tRun: {:4d}\t Turns elapsed: {:4d}\tExperience repo size: {:8d}'.format(
        itrial+1,
        irun+1,
        game.turn, 
        len(organism.experience_repo) 
      ))
      game.draw()


    organism.handle_sensor_input(game.sensors())
    organism.maintenance()

    pickle.dump(organism.experience_repo, open("organism-exprepo-manyruns.p", "wb"))

    parfrac = game.turn / game.par
    print('\tCompleted in {:4d} turns. Par {:4d}. Performance: {:.4f}'.format(game.turn, game.par, parfrac))
    print()

    trialresults.append(parfrac)
  results.append(trialresults)

print(results)



