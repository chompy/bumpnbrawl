from direct.interval.ProjectileInterval import ProjectileInterval
from direct.interval.LerpInterval import LerpScaleInterval
from direct.interval.LerpInterval import LerpPosInterval
from pandac.PandaModules import Point3
import math

class actions:

  def __init__(self, player):

    """
    Handles various actions for a player.
    """

    # Define Player
    self.player = player

    # Other Vars
    self.pickupObj = None
    self.pickupObjIsPlayer = False
    self.pickupObjPlayer = None
    self.disablePickup = False
    self.thrownObj = None
    self.origMoveSpeed = self.player.moveSpeed

  def pickup(self):

    """
    Picks up object in front of player.
    """

    if self.thrownObj: return None

    if taskMgr.hasTaskNamed("Player_" + str(self.player.id) + "_Action_Pickup"):
      if self.player.moveVal == [0,0]: self.drop()
      return None

    if self.disablePickup: return None

    pos = self.player.actor.getPos()
    tilepos = self.player.getTilePos()
    tilepos[0] += self.player.direction[0]
    tilepos[1] += self.player.direction[1]

    self.player.isMove = [False, False]
    self.player.movement = [0,0]

    for x in base.tilePositions:
      if not x['pickup']: continue
      if not x['solid']: continue
      if tilepos == x['pos']:
        x['solid'] = 0
        self.pickupObj = x['node']
        self.pickupObjIsPlayer = False
        self.player.moveSpeed = self.player.moveSpeed / 2.0
        break

    for i in range(3):
      testPos = tilepos
      for x in range(len(self.player.direction)):
        if self.player.direction[x] == 0:
          testPos[x] += (i)
          
      for x in base.players:
        if x == self.player: continue
        if x.getTilePos() == testPos:
          taskMgr.remove("Player_" + str(x.id) + "_MoveLoop")  

          self.pickupObjIsPlayer = True
          self.pickupObjPlayer = x
          self.pickupObj = x.actor
          x.isHeld = True
          self.player.moveSpeed = self.player.moveSpeed / 2.0

    if not self.pickupObj: return None

    else: 

      pos = self.player.actor.getPos()
      pos[2] += 2.0
    
      taskMgr.doMethodLater(.75, self.pickupLoop, "Player_" + str(self.player.id) + "_Action_Pickup")
      lerpPickup = LerpPosInterval(
        self.pickupObj,
        .65,
        pos
      )
      taskMgr.doMethodLater(.15, lerpPickup.start, "Player_" + str(self.player.id) + "_Action_PickupLerp", appendTask=False, extraArgs=[])

      # Move Lock
      if self.player.local:
        self.player.local = False
        pos = self.player.actor.getPos()
        for i in range(len(self.player.direction)):
          pos[i] -= self.player.direction[i] * .1
        self.player.actor.setFluidPos(pos)
        taskMgr.doMethodLater(.75, self.player.moveLock, "Player_" + str(self.player.id) + "MoveLock")

      # Pick up animation here.
      self.player.animMove = "lift-run"
      self.player.animDefault = "lift-idle"

      self.player.setAnim("lift", False)

  def pickupLoop(self, task):

    """
    Object that player pickups should follow them.
    """

    if not self.pickupObj: return task.done
    pos = self.player.actor.getPos()
    pos[2] += 2.0
    self.pickupObj.setFluidPos(pos)
    self.pickupObj.setH(self.player.actor.getH())

    return task.cont    

  def drop(self):

    """
    Drop object that player is currently carrying.
    """

    # Determine if there is a tile in front of the player.
    # We can't throw stuff past walls so.
    tilePos = self.player.getTilePos()
    tilePos2 = self.player.getTilePos()
    for i in range(len(self.player.direction)):
      tilePos[i] += self.player.direction[i]
      tilePos2[i] += self.player.direction[i] * 2.0

    for x in base.tilePositions:
      if not x['solid']: continue
      if tilePos == x['pos']: return None
      if tilePos2 == x['pos']: return None      

    # Set player speed back to original.
    self.player.moveSpeed = self.origMoveSpeed

    # Set Throwing direction.
    self.thrownDir = self.player.direction

    # If player is not carrying anything reset pickupObj.
    if not self.pickupObj: return None

    # Remove Pick up task.
    taskMgr.remove("Player_" + str(self.player.id) + "_Action_Pickup")

    # Move Lock
    if self.player.local:
      self.player.local = False
      taskMgr.doMethodLater(.35, self.player.moveLock, "Player_" + str(self.player.id) + "MoveLock")

    # Throwing Animation
    self.player.animMove = "run"
    self.player.animDefault = "idle"

    self.disablePickup = True
    taskMgr.doMethodLater(1.0, self.restorePickup, "Player_" + str(self.player.id) + "_Action_DisablePickup") 

    # If player dropped then use animation
    if self.player.movement == [0,0]:
      self.player.setAnim('throw', False)
      taskMgr.doMethodLater(.25, self.doDrop, "Player_" + str(self.player.id) + "_Action_DropDelay", appendTask=False, extraArgs=[])

    # If bump causes drop then instantly drop.
    else: self.doDrop()

  def doDrop(self):

    """
    Make actual dropping happen. (Delayed from drop method for animation).
    """

    # Use Projectile Intveral on non player objects
    if not self.pickupObjIsPlayer and self.pickupObj:
      self.throwInt = ProjectileInterval(self.pickupObj,
                         startPos = self.pickupObj.getPos(),
                         startVel = Point3(self.thrownDir[0] * 10.0, self.thrownDir[1] * 10.0, 9.0), duration = 1.4)    

      self.throwInt.start()
    
    self.thrownObj = self.pickupObj
    self.pickupObj = None

    # If not player add task to check if thrown object hits another player and then later remove it.
    if not self.pickupObjIsPlayer:
      taskMgr.doMethodLater(1.4, self.removePickup, "Player_" + str(self.player.id) + "_Action_FadePickup", extraArgs=[self.thrownObj], appendTask=False)
      taskMgr.add(self.thrownObjLoop, "Player_" + str(self.player.id) + "_Action_ThrownObjCheck")

    # If player release the player and have them move in a direction and fall down.
    else:
    
        taskMgr.add(self.pickupObjPlayer.moveLoop, "Player_" + str(self.pickupObjPlayer.id) + "_MoveLoop")
        #taskMgr.add(self.pickupObjPlayer.fallLoop, "Player_" + str(self.pickupObjPlayer.id) + "_FallLoop")
        
        self.pickupObjPlayer.moveVal = self.thrownDir
        power = self.player.power - self.pickupObjPlayer.resist
        if power < 0.0: power = 0.0
        self.pickupObjPlayer.movement = [self.thrownDir[0] * (power * 2.0), self.thrownDir[1] * (power * 2.0)]
        self.pickupObjPlayer.noCollide = self.player
        self.player.noCollide = self.pickupObjPlayer   
        self.pickupObjPlayer.isMove = [False, False]

        if self.pickupObjPlayer.local:
          self.pickupObjPlayer.local = False
          taskMgr.add(self.pickupObjPlayer.knockback, "Player_" + str(self.pickupObjPlayer.id) + "Knockback")  

        taskMgr.doMethodLater(.5, self.pickupObjPlayer.resetNoCollide, "Player_" + str(self.pickupObjPlayer.id) + "_RemoveNoCollide")
        taskMgr.doMethodLater(.5, self.player.resetNoCollide, "Player_" + str(self.player.id) + "_RemoveNoCollide")        

        self.pickupObjPlayer.reverseGravity = .25
        self.pickupObjPlayer.isHeld = False

        self.pickupObj = None
        self.thrownObj = None
        self.pickupObjPlayer = None
        self.pickupObjIsPlayer = False

        self.player.moveSpeed = self.origMoveSpeed

  def thrownObjLoop(self, task):

    """
    Manage pickupable object while it's being thrown...check collisions.
    """

    if not self.thrownObj: return task.done

    tilePos = self.thrownObj.getPos()
    for i in range(len(tilePos)):
      tilePos[i] = int(math.ceil(tilePos[i] / 2.0))
    tilePos[2] -= 1.0

    # Check if object collides with another player.
    for i in base.players:
      if i == self.player: continue
      if i.colWithBox(self.thrownObj.getPos(), (2.0, 2.0, 2.0)):
        i.moveVal = self.thrownDir
        power = self.player.power - i.resist
        if power < 0.0: power = 0.0        
        i.movement = [self.thrownDir[0] * (power), self.thrownDir[1] * (power)]
        i.isMove = [False, False]

        if i.local:
          i.local = False
          i.isKnockback = True
          taskMgr.add(i.knockback, "Player_" + str(i.id) + "Knockback")

        pos = self.thrownObj.getPos()
        self.throwInt.finish()
        self.thrownObj.setPos(pos)
        if not self.pickupObjIsPlayer:
          taskMgr.remove("Player_" + str(self.player.id) + "_Action_FadePickup")
          self.removePickup(self.thrownObj)
        self.thrownObj = None
        return task.done

    # Check if Object collide with Solid Tile
    for i in base.tilePositions:
      if not i['solid']: continue
      if i['pos'] == tilePos:
        pos = self.thrownObj.getPos()
        self.throwInt.finish()
        self.thrownObj.setPos(pos)
        self.thrownObj.setZ((i['pos'][2] * 2.0) + 2.0)
        if not self.pickupObjIsPlayer:
          taskMgr.remove("Player_" + str(self.player.id) + "_Action_FadePickup")
          self.removePickup(self.thrownObj)
        self.thrownObj = None
        return task.done

    return task.cont

  def removePickup(self, model):

    """
    Destroys a thrown pickupable object.
    """

    if not model: return None
    fade = LerpScaleInterval(model, 1.0, .1, 1.0)
    fade.start()
    taskMgr.doMethodLater(1.2, model.removeNode, "Player_" + str(self.player.id) + "_Action_DestroyPickup", extraArgs=[], appendTask=False)
    self.thrownObj = None

  def restorePickup(self, task):

    """
    Restore pickup functionality.
    """

    self.disablePickup = False
    return task.done

  def punch(self):

    """
    Punches to the object in the block directly in front of the player.
    """    

    # Can't punch if holding something
    if self.pickupObj: return None

    # Can only punch when stopped
    if not self.player.isMove == [False, False]: return None

    # Get the tile in front of the player.
    tilePos = self.player.getTilePos()
    for i in range(len(self.player.direction)):
      tilePos[i] += self.player.direction[i]

    # Loop through players to see if one is in front.
    for i in base.players:
      if i == self.player: continue

      # Player in front...hit!
      if i.getTilePos() == tilePos:

        # TODO: Punching animation here.

        # Knock player back.
        i.moveVal = self.player.direction
        i.movement = [self.player.direction[0] * ((self.player.power * 1.25) - i.resist), self.player.direction[1] * ((self.player.power * 1.25) - i.resist)]
        i.isMove = [False, False]
        if i.local:
          i.local = False
          taskMgr.add(i.knockback, "Player_" + str(i.id) + "Knockback")
      
      

    
