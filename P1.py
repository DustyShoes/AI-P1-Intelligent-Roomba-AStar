# P1.py
# Adam White
# 
# This file implements an aStarRobot robot capable of cleaning a fully-observable
# deterministic, static, discrete world.

#import threading
import queue
import heapq
from multiprocessing import Process, Queue
from collections import deque

from roomba_sim import *
from roomba_concurrent import *

goalMoves = 135
completed = False
bestSolutionMovements = []

walls = []
roomWidth = 0
roomHeight = 0

#movementQueue = queue.Queue()
fringe = []

class fringeElement(object):
    def __init__(self, weight, movements, location, dirt):
        self.weight = weight
        self.movements = movements
        self.location = location
        self.dirt = dirt
        return
    def __cmp__(self, other):
        return cmp(self.weight, other.weight)

    #delete
    def getWeight():
        return weight

def dijsktrasHeuristic(dirt):
    #TODO
    return 0

def solver(node, walls):
    (movements, location, dirt) = node
    #temperature = 115  
    #while temperature > 112: # first while loop code
    #condition = ((bestSolutionMovements == None) or (len(bestSolutionMovements) > goalMoves))
    newWeight = 0 + dijsktrasHeuristic(dirt)
    q = [] #heapq
    #f.append((newWeight, movements, location, dirt))
    heapq.heappush(q, (newWeight, movements, location, dirt))
    while (not completed) :
        #heapq.heappush(fringe, fringeElement(10, data))
        #(weight, dat) = heapq.heappop(fringe)
        #currentFringeElement = heapq.heappop(fringe)
        #item = f.pop()
        print("popping:")
        (weight, movements, location, dirt) = heapq.heappop(q)
        print("popped node: weight", weight, " movements ", movements, " location ", location, " dirt ", dirt)
        if ( dirt == [] ) :
            if (len(bestSolutionMovements) > goalMoves) :
                print("found a solution which is ", len(movements), " long. It is longer than the specified max of ", goalMoves, " long. Continuing search..")
            return movements

        if location in dirt :
            print("roomba is on top of dirt")
            #movementQueue.put('Suck')
            newDirt = copy.deepcopy(dirt) #slow #todo: this deepcopy can be eliminated, since we are returing immediately after this
            newDirt.remove(location)
            newMovements = copy.deepcopy(movements) #slow #todo: this deepcopy can be eliminated, since we are returing immediately after this
            newMovements.append('Suck')
            newWeight = len(newMovements) + dijsktrasHeuristic(newDirt) #A* heuristic
            #newFringe = (newMovements, location, newDirt)
            #heapq.heappush(fringe, (newWeight, newFringe)) here. figure out how things are stored on a fringe.
            heapq.heappush(q, (newWeight, newMovements, location, newDirt))
            continue

        (oldX, oldY) = location
        
        #East
        newX = oldX + 1
        newLocation = (newX, oldY)
        if ( not (( newLocation in walls) )) : #or (newX > roomWidth))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('East')
            newWeight = weight + 1 #len(newMovements) + dijsktrasHeuristic #A* heuristic #TODO: does this even change if nothing is sucked?
            #newFringe = (newWeight, newMovements, newLocation, dirt)
            #heapq.heappush(newFringe)
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #West
        newX = oldX - 1
        newLocation = (newX, oldY)
        if ( not ((newLocation in walls) )) : # or (newX <= 0))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('West')
            newWeight = weight + 1 #len(newMovements) + dijsktrasHeuristic #A* heuristic #TODO: does this even change if nothing is sucked?
            #newFringe = (newWeight, newMovements, newLocation, dirt)
            #heapq.heappush(newFringe)
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #North
        newY = oldY - 1
        newLocation = (oldX, newY)
        if ( not ((newLocation in walls) )) : # or (newY <= 0))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('North')
            newWeight = weight + 1 #len(newMovements) + dijsktrasHeuristic #A* heuristic #TODO: does this even change if nothing is sucked?
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #South
        newY = oldY + 1
        newLocation = (oldX, newY)
        if ( not ((newLocation in walls) )) : # or (newY > roomHeight))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('South')
            newWeight = weight + 1 #len(newMovements) + dijsktrasHeuristic #A* heuristic #TODO: does this even change if nothing is sucked?
            #newFringe = (newWeight, newMovements, newLocation, dirt)
            #heapq.heappush(newFringe)
            heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))
            
        
        

class aStarRobot(DiscreteRobot):
    #solved = false

    def initialize(self, chromosome):
        self.state = None
        startCoords = self.getRobotPosition()
        (startX, startY) = startCoords
        startLX = int(startX)
        startLY = int(startY)
        location = (startLX, startLY)
        #roomWidth = self.getRoomWidth()
        #roomHeight = self.getRoomHeight()
        firstNode = ([], location, self.getDirty())
        #heapq.heappush(fringe, firstElement)
        
        solutionMovements = solver(firstNode, self.getWalls())
  
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

