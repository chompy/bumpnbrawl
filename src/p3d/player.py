from direct.actor.Actor import Actor
from pandac.PandaModules import Texture, Camera, NodePath, OrthographicLens
from lib import basePolling
import math,random, os, specials, ConfigParser
from pandac.PandaModules import OdeWorld, OdeBody, OdeMass, Quat

GRAVITY = .5

class player:

  def __init__(self, character = "cuby", local=True, controls = False):
 
    """
    Init a player character.
    """

    # Set ID
    base.playerid += 1
    self.id = base.playerid

    # Character name
    self.character = character.strip().lower()

    # Load Animations
    charDir = os.listdir(base.assetPath + "/characters/" + character)
    animations = {}
    for filename in charDir:
      ext = filename.split(".")[len(filename.split(".")) - 1]
      filename = filename.split(".")[:len(filename.split(".")) - 1]
      if not ext == base.charExt: continue
      anim = filename[0].replace("model-", "")
      if anim.strip():
        animations[anim] = base.assetPath + "/characters/" + character + "/" + filename[0] + "." + base.charExt

    # Load Animation Configs
    self.animConfig = {}
    if os.path.exists(base.assetPath + "/characters/" + character + "/animation.ini"):
      animConfig = ConfigParser.ConfigParser()
      animConfig.read(base.assetPath + "/characters/" + character + "/animation.ini")
      for i in animConfig.sections():
        for x in animConfig.options(i):
          try:
            self.animConfig[i][x] = animConfig.getint(i, x)
          except KeyError:
            self.animConfig[i] = {}
            self.animConfig[i][x] = animConfig.getint(i, x)            
     

    # Load Model
    self.actor = Actor(base.assetPath + "/characters/" + character + "/model." + base.charExt, animations)
    self.actor.reparentTo(render)

    # Set Scale
    scale = 1.0
    if os.path.exists(base.assetPath + "/characters/" + character + "/scale.txt"):
      scale = float(open(base.assetPath + "/characters/" + character + "/scale.txt").read())
    self.actor.setScale(scale)

    # Load Texture
    skin = "default"
    texPath = base.assetPath + "/characters/" + character + "/" + skin + ".png"
    if os.path.exists(texPath):
      tex = loader.loadTexture(texPath)
      self.actor.setTexture(tex)

    # Get Dimensions of model
    self.dimensions = {}
    pos1, pos2 = self.actor.getTightBounds()   
    for i in range(len(pos1)):
      self.dimensions[i] = (pos2[i] - pos1[i]) * scale

    # Setup ODE

    self.ode_body = OdeBody(base.ode_world)

    self.ode_body.setPosition( self.actor.getPos(render) )
    self.ode_body.setQuaternion( self.actor.getQuat(render) )
    self.ode_body.addForce( (0, 200, 0) )

    self.ode_mass = OdeMass()
    self.ode_mass.setBox(1000, self.dimensions[0], self.dimensions[1], self.dimensions[2])
    self.ode_body.setMass(self.ode_mass)
    
    # Vars
    self.kbVal = [0,0]
    self.moveVal = [0,0]
    self.movement = [0,0]
    self.collision = [0,0]
    self.isMove = [False, False]
    self.tilePos = (0,0,0)
    self.fallrate = 0
    self.isKnockback = False
    self.direction = [0,-1]
    self.isHeld = False
    self.reverseGravity = 0.0
    self.noCollide = None
    self.animation = ""
    self.loopAnimation = ""
    self.isPlaying = False
    self.animDefault = "idle"
    self.animMove = "run"
    self.moveSpecial = False
    self.specialCooldown = False
    self.snapshot = None
    self.isNoReduce = False
    self.local = local
    self.doMovementLock = False

    # Set Start Position
    self.startPos = base.playerStart[self.id - 1]
    self.ode_body.setPosition(self.startPos[0], self.startPos[1], self.startPos[2] + 10.0)

    # Stats
    self.accelerate = 12000
    self.moveSpeed = 6.0
    self.power = 20.0
    self.resist = 15.0

    # Keyboard Interface
    if local:
      self.controls = controls

    # Setup Specials module which extudes the actions module.
    self.actions = specials.specials(self)
    if local:
      base.accept(self.controls['up'], self.setMoveVal, [[0,1]])
      base.accept(self.controls['down'], self.setMoveVal, [[0,-1]])
      base.accept(self.controls['left'], self.setMoveVal, [[-1,0]])
      base.accept(self.controls['right'], self.setMoveVal, [[1,0]])

      base.accept(self.controls['up'] + "-up", self.setMoveVal, [[0,.1]])
      base.accept(self.controls['down'] + "-up", self.setMoveVal, [[0,.1]])
      base.accept(self.controls['left'] + "-up", self.setMoveVal, [[.1,0]])
      base.accept(self.controls['right'] + "-up", self.setMoveVal, [[.1,0]])
      
      base.accept(self.controls['btn1'], self.actions.pickup)
      base.accept(self.controls['btn2'], self.actions.useSpecial)
    
    self.i = basePolling.Interface()

    taskMgr.add(self.moveLoop, "Player_" + str(self.id) + "_MoveLoop")   
    #taskMgr.add(self.fallLoop, "Player_" + str(self.id) + "_FallLoop")

    # Begin Animation
    self.setAnim(self.animDefault, True)

  def setMoveVal(self, kbVal):

    """
    Set keyboard values for movement.
    """

    for i in range(len(self.kbVal)):
      if kbVal[i]: self.kbVal[i] = kbVal[i]
      if kbVal[i] == .1: self.kbVal[i] = 0
    

  def moveLoop(self, task):

    """
    Moves the character.
    """

    try:
      task.lastTime
    except:
      task.lastTime = 0

    dt = task.time - task.lastTime

    # Only update every .25 seconds.
    if dt > 0.04:


      if self.doMovementLock or self.isKnockback or self.isHeld:
        self.isMove = [False, False]
      else:
        for i in range(len(self.kbVal)):
          self.moveVal[i] = self.kbVal[i]
          if self.kbVal[i]: self.isMove[i] = True
          else: self.isMove[i] = False


      pos = self.actor.getPos()

      # ODE Movement
      vel = self.ode_body.getLinearVel()
      force = [0,0,0]

      for i in range(len(self.moveVal)):
        if self.isMove[i]:
          if vel[i] * self.moveVal[i] < self.moveSpeed:
            force[i] = self.moveVal[i] * self.accelerate

        else:
        
          if vel[i] > 0.5:
            force[i] = -self.accelerate
          elif vel[i] < -0.5:
            force[i] = self.accelerate
          else:
            vel[i] = 0

      # ODE Tile Collision
      tilePos = self.getTilePos()
      pos = self.ode_body.getPosition()
      for i in base.tilePositions:
        if not i['solid']: continue

        # Below
        if i['pos'][0] == tilePos[0] and i['pos'][1] == tilePos[1] and i['pos'][2] == tilePos[2] - 1:
          vel[2] = .08
          self.ode_body.setPosition(pos[0], pos[1], tilePos[2] * 2.0)
        
        elif self.colWithTile(i['pos'] * 2.0):
          vel[0] = 0
          vel[1] = 0
          for x in range(len(self.moveVal)):
            if (i['pos'][x] * 2.0) - pos[x] < 0:
              force[x] = 20000
            else:
              force[x] = -20000
        

      if pos[2] < -10:
        self.ode_body.setPosition(self.startPos[0], self.startPos[1], self.startPos[2] + 10)


      # ODE Player Collision

      for i in base.players:
        if i == self: continue
        if i.noCollide == self or self.noCollide == i: continue

        if self.colWithNode(i.actor, i.dimensions):

          # Get Bump Power
          myPower = self.getBumpPower(i.resist)
          enePower = i.getBumpPower(self.resist)
          
          eneForce = [0,0,0]
          eneVel = [0,0,0]

          # Repel the players so they don't get stuck on each other.
          oPos = i.actor.getPos()
          for x in range(len(self.moveVal)):
            if oPos[x] - pos[x] < 0:
              force[x] = 20000
              eneForce[x] = -20000

              vel[x] = abs(enePower[x])
              eneVel[x] = -abs(myPower[x])

              if self.moveSpecial:
                vel[x] = 0
                force[x] = 50000
              elif i.moveSpecial:
                eneVel[x] = 0
                eneForce[x] = -50000
              
            else:
              force[x] = -20000
              eneForce[x] = 20000

              vel[x] = -abs(enePower[x])
              eneVel[x] = abs(myPower[x])

              if self.moveSpecial:
                vel[x] = 0
                force[x] = -50000
              elif i.moveSpecial:
                eneVel[x] = 0
                eneForce[x] = 50000


          i.ode_body.setLinearVel(eneVel[0], eneVel[1], eneVel[2])
          i.ode_body.setForce(eneForce[0], eneForce[1], eneForce[2])

          self.reduceResist()
          i.reduceResist()

          for x in range(len(myPower)):
            if abs(enePower[x]) >= 5.05:
              self.actions.drop(.5)
            if abs(myPower[x]) >= 5.05:
              i.actions.drop(.5)

          self.setNoCollide(.25, i)
          i.setNoCollide(.25, self)

      # ODE Step

      self.ode_body.setLinearVel(vel[0], vel[1], vel[2])
      self.ode_body.setForce(force[0], force[1], force[2])

      self.actor.setFluidPos(render, self.ode_body.getPosition())

      # Set Rotation [Direction]

      if not self.isKnockback and not self.isMove == [False, False]:
        self.direction = [self.moveVal[0], self.moveVal[1]]

      pos = self.actor.getPos()
      self.actor.lookAt( (pos[0] + self.direction[0], pos[1] + self.direction[1], pos[2]) )
      self.actor.setH(self.actor.getH() - 180)     

      # Animations

      # Falling
      if vel[2] < -1.0:
        self.setAnim("fall", True)

      # If moving because of a special ability.
      elif (vel[0] or vel[1]) and self.moveSpecial:
        self.setAnim("special", True)

        self.actor.lookAt( (pos[0] + self.direction[0], pos[1] + self.direction[1], pos[2]) )
        self.actor.setH(self.actor.getH() - 180)          
      
      # If moved by player the animation
      elif self.isMove[0] or self.isMove[1]:
        self.setAnim(self.animMove, True)
            
      # If knocked back by another force...
      elif (self.moveVal[0] or self.moveVal[1]) and not self.moveVal == self.direction:
        self.setAnim("bump", True)

      # Otherwise play default animation.
      else:
        self.setAnim(self.animDefault, True)
  

      task.lastTime = task.time
    return task.cont


  def knockback(self, task):

    """
    To use after a knockback. Restores controls of player
    once the players comes to a stop.
    """

    vel = self.ode_body.getLinearVel()

    if vel[0] == 0 and vel[1] == 0:
      self.doMovementLock = False
      self.isKnockback = False
      self.moveSpecial = False
      return task.done
    self.isKnockback = True
    self.doMovementLock = True
    return task.cont

  def moveLock(self, task = None, time = None):

    """
    Unlocks movement after a set amount of time.
    """

    if not task and time:
      self.doMovementLock = True
      taskMgr.doMethodLater(time, self.moveLock, "Player_" + str(self.id) + "_MoveLock", appendTask=True, extraArgs=[])
      return None

    elif task and not time:
      self.doMovementLock = False
      return task.done

  def getTilePos(self, pos = None):
    
    """
    Get player's current tile position.
    """

    if not pos:
      pos = self.actor.getPos()
    
    for i in range(len(pos)):
      pos[i] = int(math.floor( (pos[i] + (self.dimensions[i] / 2.0)) / 2.0))
        #pos[i] = int(math.floor( pos[i] / 2.0))

    return pos

  def colWithNode(self, node, size = None):

    """
    Check to see if there is a rect collision with
    another NodePath
    """

    # To get size with provided size, otherwise we'll calculate it.
    try:
      width = size[0]
      depth = size[1]
      height = size[2]
    except:
      pos1, pos2 = node.getTightBounds()     
      width = pos2[0] - pos1[0]
      depth = pos2[1] - pos1[1]
      height = pos2[2] - pos1[2]

    return self.colWithBox(node.getPos(), [width,depth,height])


  def colWithTile(self, pos):

    """
    Check to see if there is a rect collision with a tile.
    """


    return self.colWithBox(pos, [2.0,2.0,2.0])

  def colWithBox(self, pos, dimensions, myTestPos = None):

    """
    Check to see if there is a rect collision with a box.
    """

    if myTestPos: mypos = myTestPos
    else:
      mypos = self.actor.getPos()

    width = dimensions[0]
    depth = dimensions[1]
    height = dimensions[2]

    nodePos = pos

    if abs(mypos[0] - nodePos[0]) < width and abs(mypos[1] - nodePos[1]) < depth  and abs(mypos[2] - nodePos[2]) < height:
      return True

    if abs(mypos[0] - nodePos[0]) < self.dimensions[0] and abs(mypos[1] - nodePos[1]) < self.dimensions[1] and abs(mypos[2] - nodePos[2]) < self.dimensions[2]:
      return True

    return False

  def setNoCollide(self, time = None, noCollideObj = None):

    """
    Reset player no collide flag.
    """

    if time and noCollideObj:
      self.noCollide = noCollideObj
      taskMgr.doMethodLater(time, self.setNoCollide, "Player_" + str(self.id) + "_NoCollideTimer", extraArgs=[None,None])

    else:
      self.noCollide = None   

  def setAnim(self, name, loop):

    """
    Set animation.
    """

    # Set Config Vars if not set
    try:
      self.animConfig[name]
    except KeyError:
      self.animConfig[name] = {}
      self.animConfig[name]['start'] = 0
      self.animConfig[name]['end'] = self.actor.getNumFrames(name)
      self.animConfig[name]['loopfrom'] = 0
      self.animConfig[name]['loopto'] = self.actor.getNumFrames(name)

      
    # Play one time animation.
    if not loop:
      self.actor.play(name)
      self.isPlaying = True
      self.animation = name
      taskMgr.remove("Player_" + str(self.id) + "_AnimationDoneCheck")
      taskMgr.add(self.getAnimDone, "Player_" + str(self.id) + "_AnimationDoneCheck")
      return True

    # For loops... if animation is already set then no need to restart it.
    if self.animation == name: return None
    
    self.loopAnimation = name

    # Play loop as long as there is no one time animations playing.

    if not self.isPlaying:
      self.animation = name
      self.actor.loop(self.animation, restart = 0, fromFrame = self.animConfig[name]['loopfrom'], toFrame = self.animConfig[name]['loopto'])
      return True
      
    return False

  def getAnimDone(self, task):

    """
    Loops until animation is finished.
    """
    if not self.actor.getCurrentAnim():
      self.isPlaying = False
      return task.done
          
    if self.actor.getCurrentFrame(self.animation) >= self.animConfig[self.animation]['end'] - 1:
      self.isPlaying = False
      if not self.loopAnimation:
        self.setAnim(self.animDefault, True)
      else:
        self.setAnim(self.loopAnimation, True)
      
      return task.done

    return task.cont

  def getBumpPower(self, enemyResist):

    """
    Get player bump power based on enemy resist.
    """

    # Define
    power = []

    vel = self.ode_body.getLinearVel()
    # Formula
    for i in range(len(self.direction)):

      #if abs(vel[i]) > self.moveSpeed: vel[i] = self.moveSpeed

      # FORMULA!!!
      thisPower = self.moveVal[i] * (((abs(vel[i]) / 1.5) + (abs(vel[i] / (self.moveSpeed * 1.5)) * self.power)) - enemyResist)

      # Min
      if abs(thisPower) < 5.0: thisPower = 5.0 * self.moveVal[i]

      # Max
      if abs(thisPower) > 20.0:  thisPower = 20.0 * self.moveVal[i]

      power.append(thisPower)

    return power

  def reduceResist(self):

    """
    Reduce resistance after getting bumped.
    """

    if not self.isNoReduce:
      self.resist -= .5
      if self.resist < 1.0: self.resist = 1.0
      messenger.send("Player_" + str(self.id) + "_Resist_UpdateHud")
      self.noReduce(.75)

  def noReduce(self, time):

    """
    Makes it so player cannot lose resist for a set
    ammount of time.
    """

    if time > 0:
      self.isNoReduce = True
      taskMgr.doMethodLater(time, self.noReduce, "Player_" + str(self.id) + "_NoReduceTimer", extraArgs=[0])
    else:
      self.isNoReduce = False
    

  def breakFree(self, task):

    """
    Give the player a chance to break free from being picked up.
    """


    moveKeys = ['up', 'right', 'down', 'left']

    # To break free player must press the direction keys in a sequence...
    if self.i.getButton(self.controls[ moveKeys[self.breakFreeCt % 4]]):
      self.breakFreeCt -= 1
      if self.breakFreeCt <= 0:
        self.heldBy.actions.drop(1.0)
        return task.done
      
    return task.cont

  def setMovement(self, movement, isSpecial = False, canControl = True):

    """
    Instantly set the players movement.
    """

    vel = self.ode_body.getLinearVel()
    for i in range(len(self.direction)):
      vel[i] = self.direction[i] * movement

    self.ode_body.setLinearVel(vel)

    self.moveVal = self.direction
    self.moveSpecial = isSpecial
    self.isMove = [False, False]
    #self.direction = [self.moveVal[0], self.moveVal[1]]

    if not canControl:
      self.isKnockback = True
      taskMgr.add(self.knockback, "Player_" + str(self.id) + "_Knockback")

  def setSpecialCooldown(self, done = False):

    """
    Sets special to cooldown mode, special abilities cannot be used while in cooldown.
    """

    if not done:

      self.specialCooldown = True
      taskMgr.doMethodLater(base.sa_cooldown, self.setSpecialCooldown, "Player_" + str(self.id) + "_SpecialAbilityCooldown", appendTask=False, extraArgs=[True])
      messenger.send("Player_" + str(self.id) + "_Hud_SpecialAbilityCooldown")

    else:
      self.specialCooldown = False

  def takeSnapshot(self):

    """
    Returns a snapshot of this player.
    """

    if self.snapshot: return self.snapshot

    self.actor.pose("idle", 5)

    # File Name
    filename = str(self.id)

    # Width and Height
    width = 512
    height = 512

    # Make a buffer.
    tex=Texture()
    mybuffer = base.win.makeTextureBuffer('HDScreenShotBuff',width,height,tex,True)

    # Make a new camera.
    cam=Camera('SnapshotCam') 

    lens = OrthographicLens()
    lens.setFilmSize(1.1, 15)
    
    cam.setLens(lens) 
    cam.getLens().setAspectRatio(width/height) 
   
    pCam=NodePath(cam) 
      
    mycamera = base.makeCamera(mybuffer,useCamera=pCam)
    mycamera.setX(self.actor.getX() - 0.5)    
    mycamera.setZ(self.actor.getZ() - 1.75)
    mycamera.setY(self.actor.getY() - 9.0) 

    mycamera.lookAt(self.actor)

    # Set scene related stuff     
    myscene = self.actor
    mycamera.node().setScene(myscene) 

    # Generate a image.
    base.graphicsEngine.renderFrame()
    tex = mybuffer.getTexture() 
    mybuffer.setActive(False) 
    self.snapshot = tex
    base.graphicsEngine.removeWindow(mybuffer)
    #self.snapshot.write("test" + str(self.id) + ".jpg")

    return self.snapshot
