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
    taskMgr.doMethodLater(2.5, self.aiLockTarget, "Player_" + str(self.player.id) + "_AI_CheckForNewTarget", extraArgs=[])


  def ai(self, task = None):

    """
    Character AI handling.
    """

    # My position
    tilePos = self.player.getTilePos()

    # Find something to persue
    if not self.persue:
      self.aiLockTarget()
      if self.persue:
        self.persueEnd = self.persue.getTilePos()

    if not self.persue: return task.cont

    # Find a path
    if tilePos == Point3(0,0,0):
      return task.cont

    if not self.hasPath or not self.persue.getTilePos() == self.persueEnd: 
      self.findPath()
      self.pathCt = 0

    # Follow player, watch out for obstables (no pathfinding)
    enePos = self.persue.getTilePos()
    x = enePos[0] - tilePos[0]
    y = enePos[1] - tilePos[1]

    hasDir = False
    if x > 0 and not self.isObstacle([1,0]): self.aiDir = [1, 0]
    elif x < 0 and not self.isObstacle([-1,0]): self.aiDir = [-1, 0]
    elif y > 0 and not self.isObstacle([0,1]): self.aiDir = [0, 1]
    elif y < 0 and not self.isObstacle([0,-1]): self.aiDir = [0, -1]
    else:
      for x in range(-1, 1):
        for y in range(-1, 1):
          if not self.isObstacle([x, y]):
            self.aiDir = [x, y]
            break


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

  def pathGetDir(self):

    """
    Get direction based on path.
    """
    if not self.path: return None

    tilePos = self.player.getTilePos()
    minDist = 9999999999
    minItem = None
    aiDir = [0,0]

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

      if tilePos[0] - pos[0] > 0: aiDir = [-1, 0]
      elif tilePos[0] - pos[0] < 0: aiDir = [1, 0]
      if tilePos[1] - pos[1] > 0: aiDir = [0, -1]
      elif tilePos[1] - pos[1] < 0: aiDir = [0, 1]        
    except IndexError:
      1

    return aiDir
    

  def isObstacle(self, direction):

    """
    Check if there is an obstabcle in a direction.
    """

    tilePos = self.player.getTilePos()

    # Solid Wall
    if (tilePos[0] + direction[0], tilePos[1] + direction[1], tilePos[2]) in base.tileCoords:
      tile = base.tileCoords[(tilePos[0] + direction[0], tilePos[1] + direction[1], tilePos[2])]
      if tile['solid']:
        return True

    # Pitfall
    if not (tilePos[0] + direction[0], tilePos[1] + direction[1], -1) in base.tileCoords:
      return True

    # Opponent
    for i in base.players:
      if i == self.player: continue
      enePos = i.getTilePos()

      if (tilePos[0] + direction[0], tilePos[1] + direction[1]) == (enePos[0], enePos[1]):
        # Change Target
        self.aiLockTarget()
        return False

    return False
    
  def aiLockTarget(self):

    """
    Pick a target to persue.
    """
  
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


  def stopAi(self):
    taskMgr.remove("Player_" + str(self.player.id) + "_AI")    
