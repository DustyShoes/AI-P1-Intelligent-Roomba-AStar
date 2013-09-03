#
#

from roomba_sim import *

        
class ReflexRobot(Robot):
#class ReflexRobot(RealisticRobot):
  """ A ReflexRobot is a robot that uses the current percept (self.percept)
    and produces an action (self.action) without any knowledge of it's
    position, the configuration of the environment, or memory.
  """
  def runRobot(self):
    """ runRobot gets called once per timestep.  Based on the current percept
      (self.percept) (bstate, dirt) where bstate is 'Bump' or None and
      dirt is 'Dirty' or None.  It should set self.action
      to one of the robot actions (['Forward', 'TurnLeft', 'TurnRight', 'Suck']).
    """
    (bstate, dirt) = self.percepts
    # This implements the transition function.  Order matters!
    if(bstate == 'Bump'):
      self.action = ('TurnLeft',95)
    elif(dirt == 'Dirty'):
      self.action = ('Suck',None)
    else:
      self.action = ('Forward',None)
      
class RandomReflex(Robot):
  def runRobot(self):
    (bstate, dirt) = self.percepts
    # This implements the transition function.  Order matters!
    if(bstate == 'Bump'):
      self.action = ('TurnLeft',random.random() * 90 + 90)
    elif(dirt == 'Dirty'):
      self.action = ('Suck',None)
    else:
      self.action = ('Forward',None)



class ReflexRobotState(Robot):
#class ReflexRobotState(RealisticRobot):
  """ The ReflexRobotState robot is similar to the ReflexRobot, but
    state is allowed.
  """
  def __init__(self,room,speed):
    super(ReflexRobotState, self).__init__(room,speed)
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

largeEmptyRoom = RectangularRoom(50,50)
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
                    speed = 1,
                    min_coverage = 0.95,
                    num_trials = 1,
                    room = allRooms[6],
                    robot_type = RandomDiscrete,
                    ui_enable = True,
                    ui_delay = 0.1))
                    
                    
def reflexTest():
  print(runSimulation(num_robots = 1,
                    speed = 1,
                    min_coverage = 0.95,
                    num_trials = 1,
                    room = allRooms[5],
                    #robot_type = ReflexRobot,
                    #robot_type = RandomReflex,
                    robot_type = ReflexRobotState,
                    ui_enable = True,
                    ui_delay = 0.1))
                  
def testAllMaps(robot, numtrials = 10):
  score = 0
  i = 0
  for room in allRooms:
    runscore = runSimulation(num_robots = 1,
                    speed = 1,
                    min_coverage = 0.95,
                    num_trials = numtrials,
                    room = room,
                    robot_type = robot,
                    ui_enable = False,
                    ui_delay = 0.1)
    score += runscore
    print("Room %d of %d done (%d)" % (i+1, len(allRooms),runscore))
    i = i + 1
  print("Average score over %d trials: %d" % (numtrials * len(allRooms), score / len(allRooms)))
  return score / len(allRooms)
                    
if __name__ == "__main__":
  # This code will be run if this file is called on its own
  #discreteTest()
  reflexTest()
  #testAllMaps(RandomReflex, 2)
