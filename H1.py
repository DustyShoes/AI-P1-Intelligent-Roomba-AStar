#
#

from roomba_sim import *

        
#class ReflexRobot(Robot):
class ReflexRobot(RealisticRobot):
  """
    A ReflexRobot is a robot that uses the current percept (self.percept)
    and produces an action (self.action) without any knowledge of it's
    position, the configuration of the environment, or memory.
  """
  def runRobot(self):
    """ 
      runRobot gets called once per timestep.  Based on the current percept
      (self.percept) (bstate, dirt) where bstate is 'Bump' or None and
      dirt is 'Dirty' or None.  It should set self.action
      to one of the robot actions (['Forward', 'TurnLeft', 'TurnRight', 'Suck']).
    """
    (bstate, dirt) = self.percepts
    # This implements the transition function.  Order matters!
    if(bstate == 'Bump'):
      self.action = ('TurnLeft',None)
    elif(dirt == 'Dirty'):
      self.action = ('Suck',None)
    else:
      self.action = ('Forward',None)

room = RectangularRoom(20,20)
#room.occupied = zip(range(3,17), [10] * 13)

print runSimulation(num_robots = 1,
                    speed = 1,
                    min_coverage = 0.2,
                    num_trials = 1,
                    room = room,
                    robot_type = ReflexRobot,
                    ui_enable = True,
                    ui_delay = 0.1)
                    

