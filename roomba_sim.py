import math
import random
import copy

import roomba_visualize
#import pylab


REALISTIC_LEAN_MAX = 0.1  # Max degrees per timestep for lean
REALISTIC_MARBLE_PROBABILITY = 0.01  # Prob of a marble being hit in a timestep
REALISTIC_MARBLE_MAX = 10  # How much the marble rotates the robot
EDGE_REFINEMENT_STEPS = 4

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
      
    def setWall(self, (x1,y1), (x2,y2)):
      """ Draws a wall from (x1,y1) to (x2,y2) 
        Will widen wall so robot can't jump over."""
      if x1 > x2: # make sure x1 < x2
        (x1,y1,x2,y2) = (x2,y2,x1,y1)
      if x2 - x1 == 0:
        x1 -= 0.001
      dx = (x2 - x1)
      dy = (y2 - y1)
      m = dy / dx   # slope
      print "slope: " + str(m)
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
        """ Return a random position inside the room.
        returns: a Position object.
        """
        x = random.choice(range(self.width))
        y = random.choice(range(self.height))
        pos = Position(x,y)
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


class RobotBase(object):
    """
    Represents a robot cleaning a particular room.

    At all times the robot has a particular position and direction in the room.
    The robot also has a fixed speed.

    Subclasses of Robot should provide movement strategies by implementing
    updatePositionAndClean(), which simulates a single time-step.
    """
    def __init__(self, room, speed):
        """
        Initializes a Robot with the given speed in the specified room. The
        robot initially has a random direction and a random position in the
        room. The robot cleans the tile it is on.
        room:  a RectangularRoom object.
        speed: a float (speed > 0)  Using a speed > 1 will cause the robot to 
          jump over squares!
        """
        self.dir = int(360 * random.random())
        self.pos = Position(room.width * random.random(),room.height * random.random())
        self.room = room
        self.room.cleanTileAtPosition(self.pos)
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
          direction: integer representing an angle in degrees
        """
        self.dir = direction

    def updatePositionAndClean(self):
        """   Simulate the passage of a single time-step.
          Move the robot to a new position and mark the tile as needed.
        """
        raise NotImplementedError # don't change this!


           
class Robot(object):
    def __init__(self,room,speed):
        self.robot = RobotBase(room,speed)
        # Valid percepts (['Bump',None],['Dirty',None])
        self.percepts = (None,self.robot.room.tileStateAtPosition(self.robot.pos) )
        self.actions = (None,None) 
          # Valid actions (['TurnLeft', 'TurnRight', 'Forward', 'Reverse', 'Suck'],
                    #    <turn amount in degrees, speed forward/back [0..100]>)
                    #    None is default (90 degrees or 100 percent)
        
    def updatePositionAndClean(self):
        # use percepts set up during last action
        self.runRobot()
        # Do actions ['TurnLeft','TurnRight','Forward','Reverse','Suck']
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
            self.robot.last = 'Suck'
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
        
    def getRobotPosition(self):
      return self.robot.getRobotPosition()
      
    def getRobotDirection(self):
      return self.robot.getRobotDirection()
      
class RealisticRobot(Robot):
    """
    Same as Robot, but with some realistic error.
    Introduces error when moving to simulate carpet, inconsistent battery, etc.
    """
    def __init__(self,room,speed):
      """ Use Robot's init, but set a left/right lean
      """
      super(RealisticRobot, self).__init__(room,speed)
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
        



def runSimulation(num_robots, speed, min_coverage, num_trials,
                  robot_type, room, ui_enable = False, ui_delay = 0.2):
    """
    Runs NUM_TRIALS trials of the simulation and returns the mean number of
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
    """
    totaltime = 0
    num = num_trials
    max_steps = 99999.9     # Max number of steps before bailing.  Prevents endless looping.
    while num>0:
        curroom = copy.deepcopy(room) # copy room since we change it
        if ui_enable:
            anim = roomba_visualize.RobotVisualization(num_robots, curroom, delay=ui_delay)
        i = num_robots
        robots= []
        while i>0:
            robots.append(robot_type(curroom, speed))
            i -= 1
        while min_coverage * curroom.getNumTiles() > curroom.getNumCleanedTiles() and totaltime < max_steps:
            for robot in robots:
                robot.updatePositionAndClean()
            totaltime += 1
            if ui_enable:
                anim.update(curroom, robots)
                if anim.quit:
                  return float(totaltime)/num_trials
        num -= 1
        if ui_enable:
            anim.done()
    return float(totaltime)/num_trials


def showPlot1(title, x_label, y_label):
    """
    What information does the plot produced by this function tell you?
    """
    num_robot_range = range(1, 11)
    times1 = []
    times2 = []
    for num_robots in num_robot_range:
        print("Plotting", num_robots, "robots...")
        times1.append(runSimulation(num_robots, 1.0, 20, 20, 0.8, 20, StandardRobot))
        times2.append(runSimulation(num_robots, 1.0, 20, 20, 0.8, 20, RandomWalkRobot))
    pylab.plot(num_robot_range, times1)
    pylab.plot(num_robot_range, times2)
    pylab.title(title)
    pylab.legend(('StandardRobot', 'RandomWalkRobot'))
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    pylab.show()

    
def showPlot2(title, x_label, y_label):
    """
    What information does the plot produced by this function tell you?
    """
    aspect_ratios = []
    times1 = []
    times2 = []
    for width in [10, 20, 25, 50]:
        height = 300/width
        print("Plotting cleaning time for a room of width:", width, "by height:", height)
        aspect_ratios.append(float(width) / height)
        times1.append(runSimulation(2, 1.0, width, height, 0.8, 200, StandardRobot))
        times2.append(runSimulation(2, 1.0, width, height, 0.8, 200, RandomWalkRobot))
    pylab.plot(aspect_ratios, times1)
    pylab.plot(aspect_ratios, times2)
    pylab.title(title)
    pylab.legend(('StandardRobot', 'RandomWalkRobot'))
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    pylab.show()
    
