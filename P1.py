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

def getHash(location, dirt, movements):
    return str(str(location) + str(dirt) + str(len(movements)))
    #return str(location + dirt + str(len(movements)))

def isolatedDirty(totalSquares, dirt, location, movements):
    #Avoids lonely 'forgotten' spots. Quite slow.
    (roombaX, roombaY) = location
    for dirtySquare in dirt:
        (dirtyX, dirtyY) = dirtySquare
        if( abs(roombaX - dirtyX)):
            if( abs(roombaY - dirtyY)):
                
                neighbors = []
                for x in range(-2, 2) :
                    for y in range(-2, 2) :
                        neighbors.append(((dirtyX - x), (dirtyY - y)))
                for neighbor in neighbors:
                    if(neighbor in dirt):
                        return 0
    return 4

def twoClusterHeuristic(dirt):
    #Attempts to determine if there is more than one major cluster in the dirt.
    #If split into 2 clusters, we should go back and ignore this route.
    remainingDirt = copy.deepcopy(dirt)
    neighbors = {}
    #(firstDirtX, firstDirtY) = dirt.pop() #BUG! neighbors not added
    #neighbors[firstDirtX + firstDirtY * 100] = 1
    start = True
    while(len(remainingDirt) > 0):
        examineDirt = remainingDirt.pop()
        (examineDirtX, examineDirtY) = examineDirt
        if(((examineDirtX + examineDirtY * 100) in neighbors) or start):
            neighbors[examineDirtX - 2 + ((examineDirtY - 0) * 100)] = 1
            neighbors[examineDirtX - 1 + ((examineDirtY - 0) * 100)] = 1
            neighbors[examineDirtX - 1 + ((examineDirtY - 1) * 100)] = 1
            neighbors[examineDirtX - 1 + ((examineDirtY + 1) * 100)] = 1
            neighbors[examineDirtX - 0 + ((examineDirtY - 1) * 100)] = 1
            neighbors[examineDirtX - 0 + ((examineDirtY - 2) * 100)] = 1
            neighbors[examineDirtX + 1 + ((examineDirtY - 1) * 100)] = 1
            neighbors[examineDirtX + 1 + ((examineDirtY - 0) * 100)] = 1
            neighbors[examineDirtX + 2 + ((examineDirtY - 0) * 100)] = 1
            neighbors[examineDirtX + 1 + ((examineDirtY + 1) * 100)] = 1
            neighbors[examineDirtX + 0 + ((examineDirtY + 1) * 100)] = 1
            neighbors[examineDirtX + 0 + ((examineDirtY + 2) * 100)] = 1
            start = False
        else:
            #found a second cluster!
            print("dirt", dirt, " neighbors", neighbors)
            #print("found a second cluster")
            return 0
    #no extra cluster
    print("dirt", dirt, " neighbors", neighbors)
    return 0
        

#def polynomialHeuristic(totalSquares, dirt, location, movements):
def polynomialHeuristic(dirt, location):
    aboveDirt = 0
    if location in dirt:
        aboveDirt = 1

    #twoClustering = 0#twoClusterHeuristic(dirt)

    #return totalSquares - (len(dirt) * 0.2) - (aboveDirt * 0.5) - (len(movements) / .1) + twoClustering
    #return ((len(dirt) *2.000001) - 2) - (aboveDirt * 0.5)
    return ((len(dirt) * 2) - 2) + ((len(dirt))*0.00001) - (aboveDirt * 0.5)

def simpleNumDirtyHeuristic(dirt, location):
    #start = time.clock()
    #isolatedDirt = isolatedDirty(dirt, location)
    #end = time.clock()
    #print("%.2gs" % (end-start))
    
    if location in dirt :
        return (len(dirt) * 1.2) - .3
    return len(dirt) * 1.2

def dijsktrasHeuristic(dirt, location):
    #This is related to the travelling salesperson problem
    #TODO
    return 0

def solver(node, walls, heuristic, CM):
    sumTimeStart = 0;
    sumTimeOnDirt = 0;
    sumTimeMovement = 0;
    
    numExplored = 0
    overlap = 0
    explored = {}
    (movements, location, dirt) = node
    newWeight = len(movements) + heuristic(dirt, location)
    q = [] #heapq
    heapq.heappush(q, (newWeight, movements, location, dirt))
    while (CM.isCompleted() == False) :
        time1 = time.clock()
        numExplored += 1
        (weight, movements, location, dirt) = heapq.heappop(q)

        explored[getHash(location, dirt, movements)] = 1
        
        #if(len(q) > 1):
            #print("len(q) > 2000. oversize error? numExplored = ", numExplored, " weight =", weight)
        #print("popped node: weight", weight, " movements ", movements, " location ", location, " dirt ", dirt)
        #print("weight", weight, " num dirt", len(dirt))
        if ( len(dirt) <= 0 ) :
            if (len(movements) < goalMoves) :
                logging = True
                if(logging):
##                    print("")
##                    print("")
##                    print("--------STATISTICS!!! -----------")
##                    print("")
##                    print("found a solution which is ", len(movements), " long.")
##                    print("The total number of possibilities explored was ", numExplored)
##                    print("The maximum number of frontier object stored in heapq at one time was: ", " (not implemented yet)")
##                    print("")
                    print("Time start block =%.2gs" % sumTimeStart, " | on dirt =%.2gs" % sumTimeOnDirt, " | moving =%.2gs" % sumTimeMovement)
                    print("Solution len =", len(movements), " nodes explored =", numExplored)
                print("Number of identical state matches:", overlap)
                CM.storeSolution(movements)
                CM.completed = True
                return movements
            print("found a solution which is ", len(movements), " long. However, it is longer than the specified max of ", goalMoves, " long. Continuing search..")
        time2 = time.clock()
        sumTimeStart += (time2 - time2)

        #print("len(dirt) =", len(dirt), " dirt is", dirt)
        time1 = time.clock()
        if location in dirt :
            #print("roomba is on top of dirt")
            newDirt = copy.deepcopy(dirt) #slow #todo: this deepcopy can be eliminated, since we are returing immediately after this
            newDirt.remove(location)
            newMovements = movements #copy.deepcopy(movements) #slow #todo: this deepcopy can be eliminated, since we are returing immediately after this
            newMovements.append('Suck')
            newWeight = len(newMovements) + heuristic(dirt, location) #A* heuristic
            if( getHash(location, newDirt, newMovements) in explored):
                overlap += 1
                continue
            heapq.heappush(q, (newWeight, newMovements, location, newDirt))
            continue
        time2 = time.clock()
        sumTimeOnDirt += (time2 - time1)

        time1 = time.clock()
        (oldX, oldY) = location
        
        #East
        newX = oldX + 1
        newLocation = (newX, oldY)
        if ( not (( newLocation in walls) )) : #or (newX > roomWidth))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('East')
            newWeight = len(newMovements) + heuristic(dirt, location) #A* heuristic
            if(not(getHash(newLocation, dirt, newMovements) in explored)):
                overlap += 1
                heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #West
        newX = oldX - 1
        newLocation = (newX, oldY)
        if ( not ((newLocation in walls) )) : # or (newX <= 0))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('West')
            newWeight = len(newMovements) + heuristic(dirt, location) #A* heuristic
            if(not(getHash(newLocation, dirt, newMovements) in explored)):
                overlap += 1
                heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #North
        newY = oldY + 1
        newLocation = (oldX, newY)
        if ( not ((newLocation in walls) )) : # or (newY <= 0))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('North')
            newWeight = len(newMovements) + heuristic(dirt, location) #A* heuristic
            if(not(getHash(newLocation, dirt, newMovements) in explored)):
                overlap += 1
                heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))

        #South
        newY = oldY - 1
        newLocation = (oldX, newY)
        if ( not ((newLocation in walls) )) : # or (newY > roomHeight))) :
            newMovements = copy.deepcopy(movements) #slow
            newMovements.append('South')
            newWeight = len(newMovements) + heuristic(dirt, location) #A* heuristic
            if(not(getHash(newLocation, dirt, newMovements) in explored)):
                overlap += 1
                heapq.heappush(q, (newWeight, newMovements, newLocation, dirt))
        time2 = time.clock()
        sumTimeMovement += (time2 - time1)
            
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

        fullRoom = False
        if((len(self.getDirty()) / self.getNumTiles()) > 0.9):
            fullRoom = True
        print("full room ", fullRoom, " ", (self.getNumTiles() / len(self.getDirty())))

        self.CM = concurrencyManager()

        # Select the heuristic we wish to use
        #heuristic = simpleNumDirtyHeuristic
        heuristic = polynomialHeuristic
        #heuristic = dijsktrasHeuristic

        startTime = time.clock()

        #start multiple threads
        #movesQueue = Queue() #multithreaded queue. TODO This needs to be the heapq
        #solverProcess = Process(target=solver, args=(queue))
        #solverProcess.start()

        solution = solver(firstNode, self.getWalls(), heuristic, self.CM)
        #print("solution here = ", solution)
        #self.CM.storeSolution(solution)

        endTime = time.clock()
        print("%.2gs" % (endTime-startTime))
  
    def runRobot(self):
        #print("runRobot")

        if(len(self.CM.optimalSolution) <= 0):
            print("The movements array is empty. It thinks it is done.")
            dirt = self.getDirty()
            print("Finished with dirt", dirt)
            assert(0)
        
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

easyRoom = RectangularRoom(4,4)
easyRoom.setWall((2,1), (2,2))
allRooms.append(easyRoom) # [8] for debugging only, not graded

largerFullTestRoom = RectangularRoom(6,6)
largerFullTestRoom.setWall((2,2), (2,4))
allRooms.append(largerFullTestRoom) # [9] medium size full room

room10 = RectangularRoom(7,7)
#room10.setWall((1,1), (1,2))
allRooms.append(room10) # [10] 

#############################################    
def aStar():
    print(runSimulation(num_trials = 3,
                    room = allRooms[9], #Change room number here
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

