# P1.py
# Adam White
# 
# This file implements an aStarRobot robot capable of cleaning a fully-observable
# deterministic, static, discrete world.

#import threading
import queue
import heapq
from multiprocessing import Process, Queue

from roomba_sim import *
from roomba_concurrent import *

goalMoves = 135
bestSolutionMovements = None

walls = []

movementQueue = queue.Queue()
fringe = []

def solver(dirt, location, walls):
    #temperature = 115  
    #while temperature > 112: # first while loop code
    #condition = ((bestSolutionMovements == None) or (len(bestSolutionMovements) > goalMoves))
    while ((bestSolutionMovements == None) or (len(bestSolutionMovements) > goalMoves)) :
        print("things")
        item = heapq.heappop(fringe)
        (weight, movements, location, dirt) = item
        print("dirt ", dirt)
        print("start ", location)

        if location in dirt :
            print("roomba is on top of dirt")
            movementQueue.put('Suck')
            newDirt = copy.deepcopy(dirt) #slow
            newDirt.remove(location)
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('Suck')
            newWeight = len(newMovements) + dijsktrasHeuristic #A* heuristic
            newFringe = (newWeight, newMovements, location, newDirt)
            continue
        
        
    #roomWidth = self.getRoomWidth()
    #roomHeight = self.getRoomHeight()

class aStarRobot(DiscreteRobot):
    #solved = false

    def initialize(self, chromosome):
        self.state = None
        startCoords = self.getRobotPosition()
        (startX, startY) = startCoords
        startLX = int(startX)
        startLY = int(startY)
        location = (startLX, startLY)
        firstElement = (0, [], location, self.getDirty())
        heapq.heappush(fringe, firstElement)
        
        solution = solver(self.getDirty(), location, self.getWalls())
  
    def runRobot(self):
        #print("runRobot")
        (bstate, dirt) = self.percepts

        #if RobotBase.getDirty() :
        #self.action = 'Suck'
        #else :
        self.action = random.choice(['North','South','East','West'])
      
    

        
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
    #start multiple threads
    #movesQueue = Queue() #multithreaded queue.
    #solverProcess = Process(target=solver, args=(queue))
    #solverProcess.start()

    #solution = solver(self)
    
    print(runSimulation(num_trials = 2,
                    room = allRooms[0], #Change room number here
                    robot_type = aStarRobot,
                    ui_enable = True,
                    ui_delay = 0.01))
                    
                    


if __name__ == "__main__":
  # This code will be run if this file is called on its own
  #aStar()
  
  # Concurrent test execution.
  aStar()
  #concurrent_test(aStarRobot, [allRooms[0], allRooms[1], allRooms[2]], 10)
  #testAllMaps(aStarRobot, [allRooms[0], allRooms[1], allRooms[2]], 2)

