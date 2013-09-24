# P1.py
# Author: Paul Talaga
# 
# This file implements an aStarRobot robot capable of cleaning a fully-observable
# deterministic, static, discrete world.

from roomba_sim import *
from roomba_concurrent import *


class aStarRobot(DiscreteRobot):

  def initialize(self, chromosome):
    self.state = None
  
  def runRobot(self):
    (bstate, dirt) = self.percepts
    # Do lots of robot stuff here!
    self.action = random.choice(['North','South','East','West','Suck'])
    
    

        
############################################
## A few room configurations

allRooms = []

smallEmptyRoom = RectangularRoom(8,8)
allRooms.append(smallEmptyRoom)  # [0]

smallEmptyRoom2 = RectangularRoom(8,8)
smallEmptyRoom2.setWall( (4,1), (4,5) )
allRooms.append(smallEmptyRoom2) # [1]

smallEmptyRoom3 = RectangularRoom(8,8, 0.5)
smallEmptyRoom3.setWall( (4,1), (4,5) )
allRooms.append(smallEmptyRoom3) # [2]

mediumWalls1Room = RectangularRoom(20,20)
mediumWalls1Room.setWall((5,5), (15,15))
allRooms.append(mediumWalls1Room) # [3]

mediumWalls2Room = RectangularRoom(20,20)
mediumWalls2Room.setWall((5,15), (15,15))
mediumWalls2Room.setWall((5,5), (15,5))
allRooms.append(mediumWalls2Room) # [4]

mediumWalls3Room = RectangularRoom(15,15, 0.75)
mediumWalls3Room.setWall((3,3), (10,10))
mediumWalls3Room.setWall((3,10), (10,10))
mediumWalls3Room.setWall((10,3), (10,10))
allRooms.append(mediumWalls3Room) # [5]

mediumWalls4Room = RectangularRoom(30,30, 0.25)
mediumWalls4Room.setWall((7,5), (26,5))
mediumWalls4Room.setWall((26,5), (26,25))
mediumWalls4Room.setWall((26,25), (7,25))
allRooms.append(mediumWalls4Room) # [6]

mediumWalls5Room = RectangularRoom(30,30, 0.25)
mediumWalls5Room.setWall((7,5), (26,5))
mediumWalls5Room.setWall((26,5), (26,25))
mediumWalls5Room.setWall((26,25), (7,25))
mediumWalls5Room.setWall((7,5), (7,22))
allRooms.append(mediumWalls5Room) # [7]

#############################################    
def aStar():
  print(runSimulation(num_trials = 2,
                    room = allRooms[0],
                    robot_type = aStarRobot,
                    ui_enable = True,
                    ui_delay = 0.01))
                    
                    


if __name__ == "__main__":
  # This code will be run if this file is called on its own
  #aStar()
  
  # Concurrent test execution.
  concurrent_test(aStarRobot, [allRooms[0], allRooms[1], allRooms[2]], 10)
  #testAllMaps(aStarRobot, [allRooms[0], allRooms[1], allRooms[2]], 2)

