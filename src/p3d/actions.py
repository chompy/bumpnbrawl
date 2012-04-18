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

    if self.player.local: self.player.networkPosition()

    pos = self.player.actor.getPos()
    tilepos = self.player.getTilePos()
    tilepos2 = self.player.getTilePos()    
    tilepos2[0] += self.player.direction[0]
    tilepos2[1] += self.player.direction[1]

    if not self.player.moveVal == [0,0]:
      return None
    self.player.isMove = [False, False]

    for x in base.tilePositions:
      if not x['pickup']: continue
      if not x['solid']: continue
      if tilepos == x['pos'] or tilepos2 == x['pos']:
        x['solid'] = 0
        self.pickupObj = x['node']
        self.pickupObjIsPlayer = False
        self.player.moveSpeed = self.origMoveSpeed / 1.5
        break


    for i in range(3):
      testPos = tilepos2
      for x in range(len(self.player.direction)):
        if self.player.direction[x] == 0:
          testPos[x] += (i)
          
      for x in base.players:
        if x == self.player: continue
        if x.getTilePos() == testPos or x.getTilePos() == tilepos:

          # If player trying to be picked up is holding something cancel
          if x.actions.pickupObj:
            return None

          # If opponent is already held cancel.
          if x.isHeld:
            return None

          # If opponent is moving then shouldn't be able to pick them up
          vel = x.ode_body.getLinearVel()
          if abs(vel[0]) > 4.0 or abs(vel[1]) > 4.0:
            return None

          self.player.ode_body.setLinearVel( (0,0,0) )
          self.player.setNoCollide(.5, x)

          # Remove enemy move loop
          taskMgr.remove("Player_" + str(x.id) + "_MoveLoop")
          x.isOnGround = False

          # Initate break free loop...gives enemy player a chance to break free.
          x.heldBy = self.player
          x.breakFreeCt = int(math.floor(self.player.power * .75))
          taskMgr.add(x.breakFree, "Player_" + str(x.id) + "_PickUpBreakFreeLoop")

          self.pickupObjIsPlayer = True
          self.pickupObjPlayer = x
          self.pickupObj = x.actor
          x.isHeld = True
          self.player.moveSpeed = self.player.moveSpeed / 2.0

          # Hide pick up player's shadow
          self.pickupObjPlayer.shadow_node.hide()

          self.pickupObjPlayer.setAnim("fall", 1)
          break

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
      self.player.moveLock(None, .75)

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

  def drop(self, dropPower = None):

    """
    Drop object that player is currently carrying.
    """
 

    # Set player speed back to original.
    self.player.moveSpeed = self.origMoveSpeed

    # Set Throwing direction.
    self.thrownDir = [self.player.direction[0], self.player.direction[1]]

    # If player is not carrying anything reset pickupObj.
    if not self.pickupObj: return None

    # Update Player Position
    if self.player.local: self.player.networkPosition()

    # Remove Pick up task.
    taskMgr.remove("Player_" + str(self.player.id) + "_Action_Pickup")

    # Move Lock - Lock movement for ?? seconds after player is dropped
    self.player.moveLock(None, .15)

    # Throwing Animation
    self.player.animMove = "run"
    self.player.animDefault = "idle"

    self.disablePickup = True
    taskMgr.doMethodLater(1.5, self.restorePickup, "Player_" + str(self.player.id) + "_Action_DisablePickup") 

    # If player dropped then use animation
    if self.player.moveVal == [0,0]:
      self.player.setAnim('throw', False)
      taskMgr.doMethodLater(.25, self.doDrop, "Player_" + str(self.player.id) + "_Action_DropDelay", appendTask=False, extraArgs=[dropPower])

    # If bump causes drop then instantly drop.
    else: self.doDrop(dropPower)

  def doDrop(self, dropPower):

    """
    Make actual dropping happen. (Delayed from drop method for animation).
    """

    if not self.pickupObj: return None

    # Use Projectile Intveral on non player objects
    if not self.pickupObjIsPlayer and self.pickupObj:
      self.throwInt = ProjectileInterval(self.pickupObj,
                         startPos = self.pickupObj.getPos(),
                         startVel = Point3(self.thrownDir[0] * 25.0, self.thrownDir[1] * 25.0, 3.0), duration = 1.4)    

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
        
        self.pickupObjPlayer.moveVal = [self.thrownDir[0], self.thrownDir[1]]
        self.pickupObjPlayer.direction = [self.thrownDir[0], self.thrownDir[1]]

        # Get Power
        if not dropPower:
          power = ((self.player.power / self.pickupObjPlayer.resist) / .75) + 5.0
        else: power = dropPower
        
        if power < 5.0: power = 5.0
        if power > 15.0: power = 15.0

        self.pickupObjPlayer.ode_body.setPosition(self.pickupObjPlayer.actor.getPos())
        self.pickupObjPlayer.ode_body.setLinearVel(self.thrownDir[0] * (power * 1.25), self.thrownDir[1] * (power * 1.25), 3.5)
        self.pickupObjPlayer.isMove = [False, False]

        # Show pick up player's shadow
        self.pickupObjPlayer.shadow_node.show()

        self.player.setNoCollide(.5, self.pickupObjPlayer)
        self.pickupObjPlayer.setNoCollide(.5, self.player)
      
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
        i.moveVal = [self.thrownDir[0], self.thrownDir[1]]
        power = (self.player.power * 1.25) - (i.resist / 1.75)
        if power < 0.0: power = 0.0        
        i.ode_body.setLinearVel(self.thrownDir[0] * (power), self.thrownDir[1] * (power), 0)
        i.isMove = [False, False]
        i.reduceResist()

        i.isKnockback = True
        taskMgr.add(i.knockback, "Player_" + str(i.id) + "Knockback")

        pos = self.thrownObj.getPos()
        self.throwInt.finish()
        self.thrownObj.setPos(pos)
        if not self.pickupObjIsPlayer:
          taskMgr.remove("Player_" + str(self.player.id) + "_Action_FadePickup")
          self.removePickup(self.thrownObj)

        # Play Sound
        self.player.sfx['destructable'].play()
          
        self.thrownObj = None

        i.particlePlay('stars', .5)
        
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
            
        # Play Sound
        self.player.sfx['destructable'].play()
          
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

  def useSpecial(self):

    """
    Use this player's special ability.
    """

    if self.player.local: self.player.networkPosition()
    function = getattr(self, self.player.character + "_special")
    function()    

      

    
