import math,random
from pandac.PandaModules import Point3
from lib import AStar
class ai:

  def __init__(self, player):

    """
    Init!
    """

    # Vars
    self.player = player
    self.persue = None
    self.aiDir = [0,0]

    self.hasPath = False
    self.path = []
    self.cells = []
    self.pathCt = 0
    self.persueEnd = None


    self.astar = AStar.AStar(AStar.SQ_MapHandler(base.mapData,base.mapSize[0],base.mapSize[1]))
  

    # Start Loop
    taskMgr.add(self.ai, "Player_" + str(self.player.id) + "_AI")


  def ai(self, task = None):

    """
    Character AI handling.
    """

    # My position
    tilePos = self.player.getTilePos()

    # Find something to persue
    if not self.persue:
      self.aiLockTarget()
      self.persueEnd = self.persue.getTilePos()

    if not self.persue: return task.cont

    # Find a path
    if tilePos == Point3(0,0,0):
      return task.cont

    if not self.hasPath or not self.persue.getTilePos() == self.persueEnd: 
      self.findPath()
      self.pathCt = 0

    self.aiDir = [0,0]
    if self.path:

      minDist = 9999999999
      minItem = None

      for i in range(len(self.path.nodes)):
        pos = (self.path.nodes[i].location.x, self.path.nodes[i].location.y)

        if tilePos[0] == pos[0] and tilePos[1] == pos[1]:
          self.pathCt = i + 1
          break

        dist = abs(tilePos[0] - pos[0]) + abs(tilePos[1] - pos[1])
        if dist < minDist:
          self.pathCt = i
          minDist = dist

      try:
        pos = (self.path.nodes[self.pathCt].location.x, self.path.nodes[self.pathCt].location.y)

        if tilePos[0] - pos[0] > 0: self.aiDir = [-1, 0]
        elif tilePos[0] - pos[0] < 0: self.aiDir = [1, 0]
        if tilePos[1] - pos[1] > 0: self.aiDir = [0, -1]
        elif tilePos[1] - pos[1] < 0: self.aiDir = [0, 1]        
      except IndexError:
        1

      self.player.setMoveVal([.1,.1])
      if self.player.isOnGround:
        self.player.setMoveVal(self.aiDir)
    
    return task.cont


  def findPath(self):

    startPos = self.player.getTilePos()
    endPos = self.persue.getTilePos()

    start = AStar.SQ_Location(int(startPos[0]),int(startPos[1]))
    end = AStar.SQ_Location(int(endPos[0]), int(endPos[1]))

    try:
      p = self.astar.findPath(start,end)
    except AttributeError:
      return None

    if p: 
      self.hasPath = True
      self.path = p

    
  def aiLockTarget(self):
    target = None
    minDist = 9999
    
    for i in base.players:
      if i == self.player: continue
      if i.actor.getZ() < 0.0: continue

      distance = math.sqrt(  (abs(self.player.actor.getX() - i.actor.getZ()) ** 2) + (abs(self.player.actor.getY() - i.actor.getY()) ** 2))
      if distance < minDist:
        target = i
        minDist = distance

    self.persue = target
    return target

  def stopAi(self):
    taskMgr.remove("Player_" + str(self.player.id) + "_AI")    
