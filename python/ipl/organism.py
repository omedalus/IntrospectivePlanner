
from .experience_state import ExperienceState
from .reflex_action_statement import ReflexActionStatement

from .synapticle import Synapticle
from .synapton import Synapton

from .action import Action

import random
import statistics


class Organism:
  """
  Give it a Game, and watch it play!
  """

  def __init__(self, game=None):
    self.game = game
    self.exst = ExperienceState()

    synaptons = set()
    synaptons.add(Synapton('CAN_GO', Synapticle('INPUT', 'FORWARD', True)))
    synaptons.add(Synapton('GO_GO', Synapticle('CHECKED', 'CAN_GO', True), 'GO'))
    synaptons.add(Synapton('SHOULD_TURN_LEFT', Synapticle('CHECKED', 'CAN_GO', False), 'TURN LEFT'))
    synaptons.add(Synapton('DUMMY', [
      Synapticle('CHECKED', 'CAN_GO', False),
      Synapticle('CHECKED', 'CAN_GO', True)
    ], 'TURN BACK'))
    self.seed_synaptons(synaptons)
    self.fell_off_garden_path = set()


  def check_garden_path(self):
    for gp in ['CAN_GO', 'GO_GO', 'SHOULD_TURN_LEFT']:
      if gp not in self.exst.synaptons and gp not in self.fell_off_garden_path:
        print('{} got deleted!'.format(gp))
        self.fell_off_garden_path.add(gp)


  def seed_synaptons(self, synaptons):
    for s in synaptons:
      s.expectation.n = 1000000
      self.exst.synaptons[s.name] = s
      s.is_tentative = False


  def play(self, verbosity=0):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")

    if verbosity >= 1:
      print('Playing {}'.format(self.game.title))

    # Sleep-cycle maintenance phase?
    self.exst.clear()
    #self.exst.delete_sophistries()


    desperation = 0
    luxury = 0.2
    while True:
      #self.exst.start_turn()

      # Desperation slowly climbs the longer the game goes on.
      #desperation += 0.01 * (.1 - desperation)

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        if verbosity >= 1:
          print('Game state (turn {}): {}'.format(self.game.turn, gs))
        break

      self.game.set_experience(self.exst)
      self.exst.check_synaptons(100)

      # Luxury is a function of how much experimentation the organism can 
      # afford to perform. It determines the likelihood of generating new
      # synaptons. 
      # TODO: Figure out a way to integrate luxury into the reward system.
      if random.random() < luxury:
        self.exst.generate_random_synapton()

      # The odds of just performing a Hail Mary are proportional
      # to the amount of desperation being experienced by the organism.
      cmd = self.exst.choose_command(desperation, self.game.generate_random_command)
      if verbosity >= 1:
        print('{}: => Command: {}'.format(self.game, cmd))
      self.game.command(cmd)

      # The odds of generating new synaptons rise as desperation rises.
      # Organism.__generate_random_emergent_synaptomes(desperation, 0.5, self.exst, gs)

      self.exst.delete_orphaned_dependencies()
      self.check_garden_path()

      
      

  def receive_reinforcement(self, magnitude):
    self.exst.receive_reinforcement(magnitude)


      
      


