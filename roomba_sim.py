# roomba_sim.py
# Author: Paul Talaga
#
# This file provides classes and functions to simulate a Roomba-style robot in GUI and
# batch modes.  See H1.py for example robots and how these functions/classes can be 
# used.

import math
import random
import copy

import roomba_visualize


REALISTIC_LEAN_MAX = 0.1  # Max degrees per timestep for lean
REALISTIC_MARBLE_PROBABILITY = 0.01  # Prob of a marble being hit in a timestep
REALISTIC_MARBLE_MAX = 10  # How much the marble rotates the robot
EDGE_REFINEMENT_STEPS = 4

MAX_STEPS_IN_SIMULATION = 99999  # Number of time steps to allow a robot to clean a room
                                # before we give up.  Prevents runaway robots who can't
                                # clean.

class Position(object):
    """
    A Position represents a location in a two-dimensional room.
    """
    def __init__(self, x, y):
        """
        Initializes a position with coordinates (x, y).
        """
        self.x = x
        self.y = y
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getNewPosition(self, angle, speed):
        """
        Computes and returns the new Position after a single clock-tick has
        passed, with this object as the current position, and with the
        specified angle and speed.

        Does NOT test whether the returned position fits inside the room.

        angle: float representing angle in degrees, 0 <= angle < 360
        speed: positive float representing speed

        Returns: a Position object representing the new position.
        """
        old_x, old_y = self.getX(), self.getY()
        # Compute the change in position
        delta_y = speed * math.cos(math.radians(angle))
        delta_x = speed * math.sin(math.radians(angle))
        # Add that to the existing position
        new_x = old_x + delta_x
        new_y = old_y + delta_y
        return Position(new_x, new_y)   

    def __str__(self):  
        return "(%0.2f, %0.2f)" % (self.x, self.y)

class RectangularRoom(object):
    """
    A RectangularRoom represents a rectangular region containing clean or dirty
    tiles, and obstacles.

    A room has a width and a height and contains (width * height) tiles. At any
    particular time, each of these tiles is either clean or dirty.  Some tiles may
    be occupied.  Occupied tiles are considered clean.
    """
    def __init__(self, width, height):
        """
        Initializes a rectangular room with the specified width and height.
        Initially, no tiles in the room have been cleaned.
        width: an integer > 0
        height: an integer > 0
        """
        self.width = width
        self.height = height
        self.cleaned = []   # Binary dirt state
        self.occupied = []  # Binary occupation 

    def cleanTileAtPosition(self, pos):
        """
        Mark the tile under the position POS as cleaned.
        Assumes that POS represents a valid position inside this room.

        pos: a Position
        """
        x = math.floor(pos.getX())
        y = math.floor(pos.getY())
        if (x,y) not in self.cleaned:
            self.cleaned.append((x,y))
            
    def tileStateAtPosition(self,pos):
        """
        Returns 'Dirty' or None, depending on if the tile at
        pos is dirty or not.
        
        pos: a Position
        """
        x = math.floor(pos.getX())
        y = math.floor(pos.getY())
        if (x,y) in self.cleaned:
            return None
        else:
            return 'Dirty'

    def isTileCleaned(self, m, n):
        """ Return True if the tile (m, n) has been cleaned.
        Assumes that (m, n) represents a valid tile inside the room.
        m: an integer
        n: an integer
        returns: True if (m, n) is cleaned, False otherwise
        """
        return (m,n) in self.cleaned
        
    def isTileOccupied(self, m, n):
      """ Returns True if the tile (m, n) is occupied by an 
      immovable object.  Assumes m,n is in room."""
      return (m,n) in self.occupied
      
    def setWall(self, x1_y1, x2_y2):
      """ Draws a wall from (x1,y1) to (x2,y2) 
        Will widen wall so robot can't jump over."""
      x1, y1 = x1_y1
      x2, y2 = x2_y2
      if x1 > x2: # make sure x1 < x2
        (x1,y1,x2,y2) = (x2,y2,x1,y1)
      if x2 - x1 == 0:
        x1 -= 0.001
      dx = (x2 - x1)
      dy = (y2 - y1)
      m = dy / dx   # slope
      b = y1 - x1 * m
      x = x1
      (lx,ly) = (x1,x2)
      step = dx / math.sqrt(dx * dx + dy * dy)
      while x < x2:
        y = x * m + b
        blockx = math.floor(x + 0.5)
        blocky = math.floor(y + 0.5)
        self.occupied.append((blockx, blocky))
        if x != x1 and lx != blockx and ly != blocky:
          self.occupied.append((blockx-1, blocky))
        (lx, ly) = (blockx, blocky)
        x +=step

    def getNumTiles(self):
        """ Return the total number of tiles in the room.
        returns: an integer
        """
        return self.width * self.height - len(self.occupied)

    def getNumCleanedTiles(self):
        """   Return the total number of clean tiles in the room.
        returns: an integer
        """
        return len(self.cleaned)

    def getRandomPosition(self):
        """ Return a random unoccupied position inside the room.
        returns: a Position object. 
        """
        while True:
          x = random.choice(range(self.width))
          y = random.choice(range(self.height))
          pos = Position(x,y)
          if self.isPositionInRoom(pos):
            break
        return pos

    def isPositionInRoom(self, pos):
        """   Return True if pos is inside the room.
        An occupied tile is considered outside the room.
        pos: a Position object.
        returns: True if pos is in the room, False otherwise.
        """
        x = math.floor(pos.getX())
        y = math.floor(pos.getY())
        return (0 <= pos.getX() < self.width and 0 <= pos.getY() < self.height
          and not (x,y) in self.occupied)
        
    def getWidth(self):
      """   Returns the width of the room. """
      return self.width
      
    def getHeight(self):
      """   Returns the height of the room. """
      return self.height
      
    def getWalls(self):
      """ Returns a list of all immovible cells in the room.  
      Each location is a tuple (x,y)"""
      return copy.deepcopy(self.occupied) # return a copy so you can't change it!
      
    def getCleaned(self):
      """ Returns a list of all cleaned cells in the room.
      Each location is a tuple (x,y)"""
      return copy.deepcopy(self.cleaned) # return a copy so you can't change it!


class RobotBase(object):
    """
    A common robot object that contains details of the robot that an agent program
    should not have access too, thus we hide it as best as possible.

    At all times the robot has a particular position and direction in the room.
    The robot also has a fixed speed.

    Subclasses of Robot should provide movement strategies by implementing
    updatePositionAndClean(), which simulates a single time-step.
    """
    def __init__(self, room, speed, start_location = -1):
        """
        Initializes a Robot with the given speed in the specified room. The
        robot initially has a random direction and a random position in the
        room, unless a start_location (x,y) is given.  In that case the robot faces
        east.
        room:  a RectangularRoom object.
        speed: a float (speed > 0)  Using a speed > 1 will cause the robot to 
          jump over squares!
        start_location: a tuple (x,y) where the robot should start.  Default 
          direction is East (90.0 degrees)
        """
        if start_location == -1:
          self.pos = room.getRandomPosition()
          self.dir = int(360 * random.random())
        else:
          x,y = start_location
          self.pos = Position(x,y)
          self.dir = 90.0
        self.room = room
        self.last = None
        if speed > 0:
            self.speed = speed
        else:
            raise ValueError("Speed should be greater than zero")

    def getRobotPosition(self):
        """ Return the position of the robot.
          returns: a Position object giving the robot's position.
        """
        return self.pos

    def getRobotDirection(self):
        """   Return the direction of the robot.
          returns: an integer d giving the direction of the robot as an angle in
          degrees, 0 <= d < 360.
        """
        return self.dir

    def setRobotPosition(self, position):
        """ Set the position of the robot to POSITION.
          position: a Position object.
        """
        self.pos = position

    def setRobotDirection(self, direction):
        """ Set the direction of the robot to DIRECTION.
          direction: number representing an angle in degrees
        """
        self.dir = direction

    def updatePositionAndClean(self):
        """   Simulate the passage of a single time-step.
          Move the robot to a new position and mark the tile as needed.
        """
        raise NotImplementedError # don't change this!
        
    def getWalls(self):
      """ Returns a list of immovable object in the environment  (x,y)"""
      return self.room.getWalls()
      
    def getCleaned(self):
      """ Returns a list of cleaned locations in the environment (x,y)"""
      return self.room.getCleaned()
          
class ContinuousRobot(object):
    """ This class of robot lives in a continuous world where the robot can turn in any
    direction ('TurnLeft' or 'TurnRight') any number of degrees, go 'Forward' at some 
    speed (100 is full step distance), or 'Suck' dirt.  
    Deterministic environment.
    """
    def __init__(self,room,speed, start_location = -1, chromosome = None):
        self.initialize(chromosome)
        self.robot = RobotBase(room, speed, start_location)
        # Valid percepts (['Bump',None],['Dirty',None])
        self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos) )
        self.actions = (None,None) 
          # Valid actions (['TurnLeft', 'TurnRight', 'Forward', 'Suck'],
                    #    <turn amount in degrees, speed forward/back [0..100]>)
                    #    None is default (90 degrees or 100 percent)

    def initialize(self, chromosome):
      """ A hook called during __init__ """
        
    def updatePositionAndClean(self):
        # use percepts set up during last action
        self.runRobot()
        # Do actions ['TurnLeft','TurnRight','Forward','Reverse','Suck']
        # amt is degrees of turn in that direction of speed of forward 0..100
        (act, amt) = self.action
        
        if act == 'TurnLeft':
            # Will reset bump
            self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos))
            if not amt:
                amt = 90.0
            self.robot.dir = int(self.robot.dir - amt % 360)
        elif act == 'TurnRight':
            # Will reset bump
            self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos))
            if not amt:
                amt = 90.0
            self.robot.dir = int(self.robot.dir + amt % 360)
        elif act == 'Suck':
            self.robot.room.cleanTileAtPosition(self.robot.pos)
            self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos))
        elif act == 'Forward':
            if not amt:
                amt = 100.0
            newpos = self.robot.pos.getNewPosition(self.robot.dir, self.robot.speed * amt / 100.0)
            if self.robot.room.isPositionInRoom(newpos) :
                # Assume the floor is clear between here and there
                self.robot.pos = newpos
                self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos))
            else:
                # Can't take a full step, so lets try to get close
                mindist = 0
                maxdist = self.robot.speed * amt / 100.0
                for i in range(EDGE_REFINEMENT_STEPS):
                  # maxdist is too far, halfway
                  p1 = self.robot.pos.getNewPosition(self.robot.dir, (maxdist - mindist) * 1.0/2 + mindist)  # half step
                  if self.robot.room.isPositionInRoom(p1):
                    mindist = (maxdist - mindist) * 1.0/2 + mindist
                    newpos = p1 # save better point
                  else:
                    maxdist = (maxdist - mindist) * 1.0/2 + mindist
                    newpos = self.robot.pos.getNewPosition(self.robot.dir, mindist)
                self.robot.pos = newpos
                self.percepts = ('Bump',self.robot.room.tileStateAtPosition(self.robot.pos))
        else:
          raise ValueError("Unknown action: " + act)
            
        
    def runRobot(self):
      """ User needs to fill in the function.
          Use class member variables to determine next action
          Place action in self.action
      """
      raise NotImplementedError       
      
class DiscreteRobot(object):
    """ This class of robot lives in a discrete world where valid movement actions
    are North, South, East, and West.  Robot heading does not matter.  The Suck
    action will suck dirt from the current square. 
    Deterministic
    """
    def __init__(self,room,speed, start_location = -1, chromosome = None):
        self.initialize(chromosome)
        self.robot = RobotBase(room,speed, start_location)
        # Valid percepts (['Bump',None],['Dirty',None])
        self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos) )
        self.actions = (None) 
          # Valid actions ['North', 'South', 'East', 'West', 'Suck']

    def initialize(self, chromosome):
        """ A hook called during __init__ """
        
    def updatePositionAndClean(self):
        # use percepts set up during last action
        self.runRobot()
        # Do actions ['North', 'South', 'East', 'West', 'Suck']
        (act) = self.action
        if act == 'Suck':
            self.robot.room.cleanTileAtPosition(self.robot.pos)
            self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos))
            return
        elif act == 'North':
            newpos = self.robot.pos.getNewPosition(0, self.robot.speed)
        elif act == 'South':
            newpos = self.robot.pos.getNewPosition(180, self.robot.speed)
        elif act == 'East':
            newpos = self.robot.pos.getNewPosition(90, self.robot.speed)
        elif act == 'West':
            newpos = self.robot.pos.getNewPosition(270, self.robot.speed)
        else:
          raise ValueError("Unknown action: " + act)
            
        if self.robot.room.isPositionInRoom(newpos) :
          # Assume the floor is clear between here and there
          self.robot.pos = newpos
          self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos))
        else:
          # Robot doesn't move
          self.percepts = ('Bump',self.robot.room.tileStateAtPosition(self.robot.pos))           
        
    def runRobot(self):
      """ User needs to fill in the function.
          Use class member variables to determine next action
          Place action in self.action
      """
      raise NotImplementedError
        
    def getRobotPosition(self):
      return self.robot.getRobotPosition()
    
    def getWalls(self):
      return self.robot.getWalls()
      
    def getCleaned(self):
      return self.robot.getCleaned()
      
class RealisticRobot(ContinuousRobot):
    """
    Same as ContinuousRobot, but with some realistic error.
    This makes the environment  non-deterministic (stochastic)
    Introduces error when moving to simulate a slow motor and
    occasional loss of traction (hit a marble).
    """
    def __init__(self, room, speed, chromosome = None):
      """ Use Robot's init, but set a left/right lean
      """
      super(RealisticRobot, self).__init__(room, speed, chromosome = chromosome)
      self.lean = random.random() * REALISTIC_LEAN_MAX * 2 - REALISTIC_LEAN_MAX
      
    def updatePositionAndClean(self):
      """Call the superclass's same function, but fiddle with 
        direction afterwards."""
      
      super(RealisticRobot, self).updatePositionAndClean()
      # Incorporate lean
      self.robot.dir = (self.robot.dir + self.lean) % 360
      # Simulate marble or dirt
      if random.random() < REALISTIC_MARBLE_PROBABILITY:
        self.robot.dir += random.random() * REALISTIC_MARBLE_MAX
        


def meanstdv(x):
  """
  Calculate mean and standard deviation of data x[]:
      mean = {\sum_i x_i \over n}
      std = sqrt(\sum_i (x_i - mean)^2 \over n-1)
  """
  from math import sqrt
  if len(x) == 0: 
    return 99,99
  elif len(x) == 1:
    return x[0],0
  n, mean, std = len(x), 0, 0
  for a in x:
    mean = mean + a
  mean = mean / float(n)
  for a in x:
    std = std + (a - mean)**2
  std = sqrt(std / float(n-1))
  return mean, std



def runSimulation(num_robots, speed, min_coverage, num_trials,
                  robot_type, room, ui_enable = False, ui_delay = 0.2,
                  start_location = -1, debug = False, chromosome = None):
    """
    Runs NUM_TRIALS trials of the simulation and returns the (mean, std) number of
    time-steps needed to clean the fraction MIN_COVERAGE of the room.

    The simulation is run with NUM_ROBOTS robots of type ROBOT_TYPE, each with
    speed SPEED, in a ROOM.

    num_robots: an int (num_robots > 0)
    speed: a float (speed > 0) Blocks traveled per time step.  If >1, robot
                will not vacuum where it has traveled.
    min_coverage: a float (0 <= min_coverage <= 1.0)
    num_trials: an int (num_trials > 0)
    robot_type: class of robot to be instantiated (e.g. StandardRobot or
                RandomWalkRobot)
    ui_enable: set True if TK visualization is needed
    ui_delay: a float (ui_delay > 0) Time to delay between time steps.
    start_location: (x,y) a pair representing the starting position of the robot
                facing East.  Assumed to be in the environment.  
                Default is random placement.
    """
    results = []  # store per trial results for later analysis
    while num_trials>0:
        curroom = copy.deepcopy(room) # copy room since we change it
        if ui_enable:
            anim = roomba_visualize.RobotVisualization(num_robots, curroom, delay=ui_delay)
        i = num_robots
        robots= []
        while i>0:
            robots.append(robot_type(curroom, speed, start_location, chromosome))
            i -= 1
        thistime = 0
        while min_coverage * curroom.getNumTiles() > curroom.getNumCleanedTiles() and thistime < MAX_STEPS_IN_SIMULATION:
            for robot in robots:
                robot.updatePositionAndClean()
            thistime += 1
            if ui_enable:
                anim.update(curroom, robots)
                if anim.quit:
                  results.append(thistime)
                  return meanstdv(results)
        num_trials -= 1
        if debug: print(thistime)
        results.append(thistime)
        if ui_enable:
            anim.done()
    return meanstdv(results)
    
def testAllMaps(robot, rooms, numtrials = 10, start_location = -1, chromosome = None):
  """ Runs the specified robot over the list of rooms, optionally with a specified
  number of trials per map, and starting location (x,y).
  Prints status to the screen and returns the average performance over all maps and 
  trials."""
  score = 0
  i = 0
  for room in rooms:
    runscore, runstd = runSimulation(num_robots = 1,
                    speed = 1,
                    min_coverage = 0.95,
                    num_trials = numtrials,
                    room = room,
                    robot_type = robot,
                    start_location = start_location,
                    #debug = True,
                    chromosome = chromosome,
                    ui_enable = False)
    score += runscore
    print("Room %d of %d done (score: %d std: %d)" % (i+1, len(rooms), runscore, runstd))
    i = i + 1
  print("Average score over %d trials: %d" % (numtrials * len(rooms), score / len(rooms)))
  return score / len(rooms)
  
# Print text if this file was run on its own.  
if __name__ == "__main__":
   print("No example robots implemented.  See H1.py for examples of usage.")
    
