# P1.py
# Adam White
# 
# This file implements an aStarRobot robot capable of cleaning a fully-observable
# deterministic, static, discrete world.

#import threading
import heapq
from multiprocessing import Process, Queue

from roomba_sim import *
from roomba_concurrent import *

goalMoves = 135
#heuristic = None #which heuristic method to use

class concurrencyManager(object):
    def __init__(self):
        self.completed = False # Whether we have found the solution. Kill other threads if true.
        self.optimalSolution = [] # Stores the optimal solution

    def storeSolution(self, solution):
        for move in solution:
            self.optimalSolution.append(move)

    def isCompleted(self):
        return self.completed

def simpleNumDirtyHeuristic(dirt, location):
    #Just returns the amount of dirt left
    if location in dirt :
        return (len(dirt) * 1.5) - .3
    return len(dirt) * 1.5

def dijsktrasHeuristic(dirt, location):
    #This is related to the travelling salesperson problem
    #TODO
    return 0

def solver(node, walls, heuristic, CM):
    numExplored = 0
    (movements, location, dirt) = node
    newWeight = 0 + heuristic(dirt, location)
    q = [] #heapq
    heapq.heappush(q, (newWeight, movements, location, dirt))
    while (len(dirt) > 0 and CM.isCompleted() == False) :
        numExplored += 1
        (weight, movements, location, dirt) = heapq.heappop(q)
        #print("popped node: weight", weight, " movements ", movements, " location ", location, " dirt ", dirt)
        if ( len(dirt) <= 0 ) :
            if (len(movements) < goalMoves) :
                logging = False
                if(logging):
                    print("")
                    print("")
                    print("--------STATISTICS!!! -----------")
                    print("")
                    print("found a solution which is ", len(movements), " long.")
                    print("The total number of possibilities explored was ", numExplored)
                    print("The maximum number of frontier object stored in heapq at one time was: ", " (not implemented yet)")
                    print("")
                CM.storeSolution(movements)
                CM.completed = True
                return movements
            print("found a solution which is ", len(movements), " long. However, it is longer than the specified max of ", goalMoves, " long. Continuing search..")

        if location in dirt :
            #print("roomba is on top of dirt")
            newDirt = copy.deepcopy(dirt) #slow #todo: this deepcopy can be eliminated, since we are returing immediately after this
            newDirt.remove(location)
            newMovements = movements #copy.deepcopy(movements) #slow #todo: this deepcopy can be eliminated, since we are returing immediately after this
            newMovements.append('Suck')
            newWeight = len(newMovements) + heuristic(newDirt, location) #A* heuristic
            heapq.heappush(q, (newWeight, newMovements, location, newDirt))
            continue

        (oldX, oldY) = location
        
        #East
        newX = oldX + 1
        newLocation = (newX, oldY)
        if ( not (( newLocation in walls) )) : #or (newX > roomWidth))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('East')
            newWeight = weight + 1 + heuristic(dirt, newLocation) #A* heuristic 
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #West
        newX = oldX - 1
        newLocation = (newX, oldY)
        if ( not ((newLocation in walls) )) : # or (newX <= 0))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('West')
            newWeight = weight + 1 + heuristic(dirt, newLocation) #A* heuristic 
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #North
        newY = oldY + 1
        newLocation = (oldX, newY)
        if ( not ((newLocation in walls) )) : # or (newY <= 0))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('North')
            newWeight = weight + 1 + heuristic(dirt, newLocation) #A* heuristic 
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #South
        newY = oldY - 1
        newLocation = (oldX, newY)
        if ( not ((newLocation in walls) )) : # or (newY > roomHeight))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('South')
            newWeight = weight + 1 + heuristic(dirt, newLocation) #A* heuristic 
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))
            
    print("Something went wrong and no solution was found")
    assert(0)
    

        
class aStarRobot(DiscreteRobot, concurrencyManager):
    
    def initialize(self, chromosome):
        self.state = None
        startCoords = self.getRobotPosition()
        (startX, startY) = startCoords
        startLX = int(startX)
        startLY = int(startY)
        location = (startLX, startLY)
        firstNode = ([], location, self.getDirty())

        self.CM = concurrencyManager()

        # Select the heuristic we wish to use
        heuristic = simpleNumDirtyHeuristic
        #heuristic = dijsktrasHeuristic

        #start multiple threads
        #movesQueue = Queue() #multithreaded queue. TODO This needs to be the heapq
        #solverProcess = Process(target=solver, args=(queue))
        #solverProcess.start()

        solution = solver(firstNode, self.getWalls(), heuristic, self.CM)
        #print("solution here = ", solution)
        #self.CM.storeSolution(solution)
  
    def runRobot(self):
        #print("runRobot")

##        if(len(self.CM.optimalSolution) <= 0):
##            print("The movements array is empty. It thinks it is done.")
##            dirt = self.getDirty()
##            print("Finished with dirt", dirt)
##            assert(0)
        
        nextMovement = self.CM.optimalSolution.pop(0)
        self.action = nextMovement
        return
      
    

        
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

easyRoom = RectangularRoom(6,6,0.5)
easyRoom.setWall((2,2), (2,4))
allRooms.append(easyRoom) # [8] for debugging only, not graded

#############################################    
def aStar():
    print(runSimulation(num_trials = 1,
                    room = allRooms[1], #Change room number here
                    robot_type = aStarRobot,
                    ui_enable = True,
                    ui_delay = 0.1))
                    
                    


if __name__ == "__main__":
  # This code will be run if this file is called on its own
  #aStar()
  
  # Concurrent test execution.
  aStar()
  #concurrent_test(aStarRobot, [allRooms[0], allRooms[1], allRooms[2]], 10)
  #testAllMaps(aStarRobot, [allRooms[0], allRooms[1], allRooms[2]], 2)

