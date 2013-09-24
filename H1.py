# H1.py
# Author: Paul Talaga
# 
# This file demonstrates how to implement various kinds of Roomba robot agents
# and run them in GUI or non-gui mode using the roomba_sim library.
#

from roomba_sim import *
from roomba_concurrent import *

# Each robot below should be a subclass of ContinuousRobot, RealisticRobot, or DiscreteRobot.
# All robots need to implement the runRobot(self) member function, as this is where
# you will define that specific robot's characteristics.

# All robots perceive their environment through self.percepts (a class variable) and 
# act on it through self.action.  The specific percepts received and actions allowed
# are specific to the superclass.  See roomba_sim for details.

# ContinuousRobot - Deterministic continuous environment - Same percepts/actions as
#                     RealisticRobot
# RealisticRobot  - Non-deterministic continuous environment - Same percepts/actions as
#                     ContinuousRobot
# DiscreteRobot   - Deterministic discrete environment
        
class ReflexRobot(ContinuousRobot):
#class ReflexRobot(RealisticRobot):
  """ A ReflexRobot is a robot that uses the current percept (self.percept)
    and produces an action (self.action) without any knowledge of it's
    position, the configuration of the environment, or memory.
  """
  def initialize(self, chromosome):
    self.degrees = chromosome

  def runRobot(self):
    """ runRobot gets called once per timestep.  Based on the current percept
      (self.percept) (bstate, dirt) where bstate is 'Bump' or None and
      dirt is 'Dirty' or None.  It should set self.action
      to one of the robot actions (['Forward', 'TurnLeft', 'TurnRight', 'Suck']).
    """
    (bstate, dirt) = self.percepts
    # This implements the transition function.  Order matters!
    if(bstate == 'Bump'):
      self.action = ('TurnLeft', self.degrees)
    elif(dirt == 'Dirty'):
      self.action = ('Suck',None)
    else:
      self.action = ('Forward',None)
      
      
      
class RandomReflex(ContinuousRobot):
  def runRobot(self):
    (bstate, dirt) = self.percepts
    # This implements the transition function.  Order matters!
    if(bstate == 'Bump'):
      self.action = ('TurnLeft',random.random() * 10 + 45)
    elif(dirt == 'Dirty'):
      self.action = ('Suck',None)
    else:
      self.action = ('Forward',None)



class ReflexRobotState(ContinuousRobot):
#class ReflexRobotState(RealisticRobot):
  """ The ReflexRobotState robot is similar to the ReflexRobot, but
    state is allowed.
  """
  def __init__(self,room,speed, start_location = -1):
    super(ReflexRobotState, self).__init__(room,speed, start_location)
    # Set initial state here
    self.state = 0
    
  def runRobot(self):
    """ If we went forward 5 times and didn't see dirt, turn some.
    """
    (bstate, dirt) = self.percepts
    if(bstate == 'Bump'):
      self.action = ('TurnLeft',95)
    elif(dirt == 'Dirty'):
      self.action = ('Suck',None)
      self.state = 0
    elif(self.state >=5):
      # turn some
      self.action = ('TurnLeft',45)
      self.state = 0
    else:
      self.action = ('Forward',None)
      self.state = self.state + 1


class RandomDiscrete(DiscreteRobot):
  """ RandomDiscrete is a robot that simply shows the use of random
    actions in a discrete world.
  """
  def runRobot(self):
    (bstate, dirt) = self.percepts
    # This picks a random action from the following list
    self.action = random.choice(['North','South','East','West','Suck'])
        
############################################
## A few room configurations

allRooms = []

smallEmptyRoom = RectangularRoom(10,10)
allRooms.append(smallEmptyRoom)  # [0]

largeEmptyRoom = RectangularRoom(10,10)
allRooms.append(largeEmptyRoom) # [1]

mediumWalls1Room = RectangularRoom(30,30)
mediumWalls1Room.setWall((5,5), (25,25))
allRooms.append(mediumWalls1Room) # [2]

mediumWalls2Room = RectangularRoom(30,30)
mediumWalls2Room.setWall((5,25), (25,25))
mediumWalls2Room.setWall((5,5), (25,5))
allRooms.append(mediumWalls2Room) # [3]

mediumWalls3Room = RectangularRoom(30,30)
mediumWalls3Room.setWall((5,5), (25,25))
mediumWalls3Room.setWall((5,15), (15,25))
mediumWalls3Room.setWall((15,5), (25,15))
allRooms.append(mediumWalls3Room) # [4]

mediumWalls4Room = RectangularRoom(30,30)
mediumWalls4Room.setWall((7,5), (26,5))
mediumWalls4Room.setWall((26,5), (26,25))
mediumWalls4Room.setWall((26,25), (7,25))
allRooms.append(mediumWalls4Room) # [5]

mediumWalls5Room = RectangularRoom(30,30)
mediumWalls5Room.setWall((7,5), (26,5))
mediumWalls5Room.setWall((26,5), (26,25))
mediumWalls5Room.setWall((26,25), (7,25))
mediumWalls5Room.setWall((7,5), (7,22))
allRooms.append(mediumWalls5Room) # [6]

#############################################    
def discreteTest():
  print(runSimulation(num_robots = 1,
                    min_clean = 0.95,
                    num_trials = 1,
                    room = allRooms[6],
                    robot_type = RandomDiscrete,
                    ui_enable = True,
                    ui_delay = 0.1))
                    
                    
def reflexTest():
  print(runSimulation(num_robots = 1,
                    min_clean = 0.95,
                    num_trials = 2,
                    room = allRooms[5],
                    robot_type = ReflexRobot,
                    #robot_type = RandomReflex,
                    #robot_type = ReflexRobotState,
                   # start_location = (5,5),
                   # ui_enable = True,
                    chromosome = 91,
                    ui_delay = 0.001))


if __name__ == "__main__":
  # This code will be run if this file is called on its own
  #discreteTest()
  #reflexTest()
  
  # Concurrent test execution.
  print(concurrent_test(ReflexRobot, allRooms, num_trials = 10, min_clean = 0.95, chromosome = 91))

  # Sequential test execution.
  #testAllMaps(ReflexRobot, allRooms, 5, (5,5), 90)

  #testAllMaps(RandomReflex, allRooms, 2,(5,5))
  #testAllMaps(RandomDiscrete, allRooms, 20, (5,5))
