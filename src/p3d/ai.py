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
    self.persueTarget = "player"


    self.astar = AStar.AStar(AStar.SQ_MapHandler(base.mapData,base.mapSize[0],base.mapSize[1]))
  

    # Start Loop
    taskMgr.add(self.ai, "Player_" + str(self.player.id) + "_AI")
    taskMgr.doMethodLater(2.5, self.aiLockTarget, "Player_" + str(self.player.id) + "_AI_CheckForNewTarget")


  def ai(self, task = None):

    """
    Character AI handling.
    """

    # My position
    tilePos = self.player.getTilePos()

    # Find something to persue
    if not self.persue:
      self.aiLockTarget()

    if not self.persue: return task.cont

    # Find a path
    if tilePos == Point3(0,0,0):
      return task.cont

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
      hasDir = False
      for x in range(-1, 1):
        for y in range(-1, 1):
          if not self.isObstacle([x, y]):
            self.aiDir = [x, y]
            hasDir = True
            break
        if hasDir: break

  
    # Try picking up
    if not self.player.actions.pickupObj:    
      if (int(tilePos[0]) + self.aiDir[0], int(tilePos[1]) + self.aiDir[1], int(tilePos[2])) in base.tileCoords:
        tile = base.tileCoords[( int(tilePos[0]) + self.aiDir[0], int(tilePos[1]) + self.aiDir[1], int(tilePos[2]))]
        if tile['pickup'] and tile['solid']:
          self.player.actions.pickup()
          self.aiDir = [0,0]
          if self.player.actions.pickupObj:          
            taskMgr.doMethodLater(.75, self.player.actions.pickup, "Player_" + str(self.player.id) + "_AI_DropObject", extraArgs=[])

    # Persuer falls off
    if self.persue and self.persue.actor.getZ() < 0.0:
      self.aiLockTarget()

    # Use Special

    # Offensive Special
    if self.player.special_type == "offense" and self.persue and not self.player.specialCooldown:
      eneTile = self.persue.getTilePos()

      for x in range(0,1):
        if eneTile[x] == tilePos[x]:
          if x == 0: y = 1
          else: y = 0
          
          if abs(eneTile[y] - tilePos[y]) < self.player.special_range and abs(eneTile[y] - tilePos[y]) > self.player.special_minRange:
            # Use Special
            myDir = [0,0]
            if eneTile[0] - tilePos[0] > 0: myDir[0] = 1
            elif eneTile[0] - tilePos[0] < 0: myDir[0] = -1
            if eneTile[1] - tilePos[1] > 0: myDir[1] = 1
            elif eneTile[1] - tilePos[1] < 0: myDir[1] = -1

            self.player.direction = myDir 
            self.player.actions.useSpecial()

    # Evade attacks

    for i in base.players:
      if i == self.player: continue
      if i.actor.getZ() < 0.0: continue

      # Only defend fast movement attacks
      vel = i.ode_body.getLinearVel()
      if not abs(vel[0]) > 6.0 and not abs(vel[1]) > 6.0: continue

      # Get Distance
      distance = math.sqrt(  (abs(self.player.actor.getX() - i.actor.getX()) ** 2) + (abs(self.player.actor.getY() - i.actor.getY()) ** 2))

      # Defensive Special
      if not self.player.specialCooldown and abs(distance) < self.player.special_range and abs(distance) > self.player.special_minRange:
        
        eneTile = i.getTilePos()
        
        # Use Special
        myDir = [0,0]
        if eneTile[0] - tilePos[0] > 0: myDir[0] = 1
        elif eneTile[0] - tilePos[0] < 0: myDir[0] = -1
        if eneTile[1] - tilePos[1] > 0: myDir[1] = 1
        elif eneTile[1] - tilePos[1] < 0: myDir[1] = -1

        self.player.direction = myDir 
        self.player.actions.useSpecial()

      # Sidestep
      else:
        if abs(distance) < 8.0:
          eneTile = i.getTilePos()
          myDir = [0,0]
          if eneTile[0] - tilePos[0] > 0: myDir[0] = 1
          elif eneTile[0] - tilePos[0] < 0: myDir[0] = -1
          if eneTile[1] - tilePos[1] > 0: myDir[1] = 1
          elif eneTile[1] - tilePos[1] < 0: myDir[1] = -1          

          for x in range(len(myDir)):
            if not myDir[x]:
              for y in range(-1,1):
                if y == 0: continue
                myDir[x] = y
                if not self.isObstacle(myDir):
                  self.aiDir = myDir
                  break
              break
    

    self.player.setMoveVal([.1,.1])

    if self.player.actor.getZ() < 0.0:
      self.aiLockTarget()
      self.player.actions.drop()
      self.aiDir = [0,0]
      return task.cont
    
    if self.player.isOnGround and self.persue and not self.persue.actor.getZ() < 0.0:
      self.player.setMoveVal(self.aiDir)
    
    return task.cont


  def findPath(self, endPos):

    startPos = self.player.getTilePos()

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
      if tile['pickup']:
        if not self.player.actions.pickupObj:
          return False
        else:
          return True
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

  def findNearbyPit(self):

    """
    Checks to see if pit is nearby.
    """
    
    tilePos = self.player.getTilePos()
    for x in range(-5, 5):
      for y in range(-5, 5):
        if not (tilePos[0] + x, tilePos[1] + y, -1) in base.tileCoords:
          return (tilePos[0] + x, tilePos[1] + y)

    return None
    
  def aiLockTarget(self, task = None):

    """
    Pick a target to persue.
    """

    if not self.persueTarget == "player": return None
  
    target = None
    minDist = 9999
    
    for i in base.players:
      if i == self.player: continue
      if i.actor.getZ() < 0.0: continue

      distance = math.sqrt(  (abs(self.player.actor.getX() - i.actor.getX()) ** 2) + (abs(self.player.actor.getY() - i.actor.getY()) ** 2))
      if distance < minDist:
        target = i
        minDist = distance

    self.persue = target

    if task: return task.again

  def stopAi(self):
    taskMgr.remove("Player_" + str(self.player.id) + "_AI")    
