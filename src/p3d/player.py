from direct.actor.Actor import Actor
from pandac.PandaModules import Texture, Camera, NodePath, OrthographicLens, TransparencyAttrib, CardMaker, TextureStage, Vec3, VBase3
from direct.gui.OnscreenText import OnscreenText,TextNode 
from direct.particles.ParticleEffect import ParticleEffect
from direct.interval.LerpInterval import LerpColorScaleInterval, LerpPosInterval,LerpScaleInterval
from direct.interval.IntervalGlobal import *
from lib import basePolling
import math,random, os, specials, ConfigParser, ai
from pandac.PandaModules import OdeWorld, OdeBody, OdeMass, Quat

# Load Sounds
from direct.showbase import Audio3DManager

GRAVITY = .5

class player:

  def __init__(self, character = "cuby", local=True, controls = 0, onlineId = None):
 
    """
    Init a player character.
    """

    # Set ID
    base.playerid += 1
    self.id = base.playerid

    # Set Online ID
    self.onlineId = onlineId

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
    self.actor.setTransparency(TransparencyAttrib.MAlpha)

    # Set Scale
    scale = 1.0
    if os.path.exists(base.assetPath + "/characters/" + character + "/scale.txt"):
      scale = float(open(base.assetPath + "/characters/" + character + "/scale.txt").read())
    self.actor.setScale(scale)

    # Z Offset
    self.zOffset = 0
    if os.path.exists(base.assetPath + "/characters/" + character + "/zoffset.txt"):
      self.zOffset = float(open(base.assetPath + "/characters/" + character + "/zoffset.txt").read()) 

    # AI Special Characteristics
    self.special_type = "offense"
    if os.path.exists(base.assetPath + "/characters/" + character + "/ai_special.txt"):
      aiSpecial = open(base.assetPath + "/characters/" + character + "/ai_special.txt").read().strip().split("\n")
      self.special_type = aiSpecial[0].lower().strip()
      self.special_range = float(aiSpecial[1].strip())
      self.special_minRange = float(aiSpecial[2].strip()) 

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

    self.dimensions = [1.25,1.25,1.0]

    # Load 3D Sounds
    #self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
    self.sfx = {
      'bump'            :   base.loader.loadSfx(base.assetPath + "/sfx/bump.wav"),
      'special'         :   base.loader.loadSfx(base.assetPath + "/sfx/special.wav"),
      'lunge'           :   base.loader.loadSfx(base.assetPath + "/sfx/lunge.wav"),
      'destructable'    :   base.loader.loadSfx(base.assetPath + "/sfx/destructable.wav"), 
    }
    
    #for i in self.sfx:
    #  self.audio3d.attachSoundToObject(self.sfx[i], self.actor)

    # Setup Shadow
    shadow = CardMaker("Player_" + str(self.id) + "_Shadow")
    shadow.setFrame(-1.25,1.25,-1.25,1.25)
    shadow.setColor(1,1,1,1)
    shadow_node = render.attachNewNode(shadow.generate())
    shadow_node.setTransparency(TransparencyAttrib.MAlpha)   
    shadow_node.setPos(self.actor.getPos())
    shadow_node.setP(-90)

    shadow_tex = loader.loadTexture(base.assetPath + "/characters/shadow.png")
    shadow_node.setTexture(shadow_tex)
    shadow_node.setScale(.5)
    self.shadow_node = shadow_node

    # Setup ODE

    self.ode_body = OdeBody(base.ode_world)

    self.ode_body.setPosition( self.actor.getPos() )
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
    self.snapshot = loader.loadTexture(base.assetPath + "/characters/" + character + "/picture.jpg")
    self.isNoReduce = False
    self.local = local
    self.doMovementLock = False
    self.isDead = False
    self.showDashCloud = True
    self.isOnGround = False
    self.ai = None

    # Set Start Position
    self.startPos = base.playerStart[ (self.id % len(base.playerStart)) - 1]
    self.ode_body.setPosition(self.startPos[0], self.startPos[1], self.startPos[2] + 20.0 )

    # Stats
    self.accelerate = 100000

    # Load stats from external file...
    if os.path.exists(base.assetPath + "/characters/" + character + "/stats.txt"): 
      statFile = open(base.assetPath + "/characters/" + character + "/stats.txt").read().split("\n")

      self.moveSpeed = 5.0 + ( float(statFile[0].split(" ")[0]) )
      self.power = 5.0 + (float(statFile[1].split(" ")[0]) * 5.0)
      self.resist = 5.0 + (float(statFile[2].split(" ")[0]) * 5.0)

    else:
      self.moveSpeed = 5.0
      self.power = 10.0
      self.resist = 5.0

    self.maxResist = self.resist

    # Keyboard Interface
    self.controls = str(controls)

    # Setup Specials module which extudes the actions module.
    self.actions = specials.specials(self)

    if self.local:
      base.accept("p" + self.controls + "_up", self.setMoveVal, [[0,1]])
      base.accept("p" + self.controls + "_down", self.setMoveVal, [[0,-1]])
      base.accept("p" + self.controls + "_left", self.setMoveVal, [[-1,0]])
      base.accept("p" + self.controls + "_right", self.setMoveVal, [[1,0]])

      base.accept("p" + self.controls + "_up-up", self.setMoveVal, [[0,.1]])
      base.accept("p" + self.controls + "_down-up", self.setMoveVal, [[0,.1]])
      base.accept("p" + self.controls + "_left-up", self.setMoveVal, [[.1,0]])
      base.accept("p" + self.controls + "_right-up", self.setMoveVal, [[.1,0]])
      
      base.accept("p" + self.controls + "_btna", self.actions.jump)
      base.accept("p" + self.controls + "_btnb", self.actions.useSpecial)   

      # Position Send
      taskMgr.doMethodLater(1.5, self.networkPosition, "Player_+ " + str(self.id) + "_SendPositionToNetwork")
       
    else:
      base.accept(str(self.onlineId) + "p" + self.controls + "_up", self.setMoveVal, [[0,1]])

      base.accept(str(self.onlineId) + "p" + self.controls + "_down", self.setMoveVal, [[0,-1]])
      base.accept(str(self.onlineId) + "p" + self.controls + "_left", self.setMoveVal, [[-1,0]])
      base.accept(str(self.onlineId) + "p" + self.controls + "_right", self.setMoveVal, [[1,0]])

      base.accept(str(self.onlineId) + "p" + self.controls + "_up-up", self.setMoveVal, [[0,.1]])
      base.accept(str(self.onlineId) + "p" + self.controls + "_down-up", self.setMoveVal, [[0,.1]])
      base.accept(str(self.onlineId) + "p" + self.controls + "_left-up", self.setMoveVal, [[.1,0]])
      base.accept(str(self.onlineId) + "p" + self.controls + "_right-up", self.setMoveVal, [[.1,0]])
      
      base.accept(str(self.onlineId) + "p" + self.controls + "_btna", self.actions.pickup)
      base.accept(str(self.onlineId) + "p" + self.controls + "_btnb", self.actions.useSpecial)
    
    self.i = basePolling.Interface()

    taskMgr.doMethodLater(1.5, self.moveLoop, "Player_" + str(self.id) + "_MoveLoop")   

    # Misc Models
    self.dash_cloud = loader.loadModel(base.assetPath + "/misc_models/dash_cloud." + base.charExt )
    self.dash_cloud.reparentTo(render)
    self.dash_cloud.setTransparency(TransparencyAttrib.MAlpha)
    self.dash_cloud.hide()

    self.land_cloud = loader.loadModel(base.assetPath + "/misc_models/landing_cloud." + base.charExt )
    self.land_cloud.reparentTo(render)
    self.land_cloud.setTransparency(TransparencyAttrib.MAlpha)
    self.land_cloud.setTwoSided(True)
    self.land_cloud.hide()

    # +1 Text
    self.getKill = OnscreenText("+1",1,fg=(1,0,0,1),pos=(0,2),align=TextNode.ACenter,scale=1.0 / self.actor.getScale()[0],mayChange=1, parent=self.actor) 
    self.getKill.setBillboardPointWorld()
    self.getKill.hide()

    self.killLerp = Parallel(
      LerpPosInterval(self.getKill, 1.5, (0,0,2), (0,0,0)),
      LerpColorScaleInterval(self.getKill, 1.5, (1,1,1,0), (1,1,1,1))
    )

    self.killCount = 0
    self.lastHit = None
  
    # Begin Animation
    self.setAnim(self.animDefault, True)

  def activateAi(self):
    if not self.ai:
      self.ai = ai.ai(self)
    else:
      self.ai.__init__(self)

  def deactivateAi(self):
    self.ai.stopAi()

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


      if self.doMovementLock or self.isHeld:
        self.isMove = [False, False]
      else:
        for i in range(len(self.kbVal)):
          self.moveVal[i] = self.kbVal[i]
          if self.kbVal[i]:

            # If was not previously moving... 
            # Show the dash cloud!
            if not self.isMove[0] and not self.isMove[1] and self.showDashCloud and self.isOnGround and not self.isKnockback:

              dpos = self.actor.getPos()
              dpos[2] -= (self.dimensions[2] / 2.0)
              dEndPos = self.actor.getPos()
              dEndPos[2] -= (self.dimensions[2] / 2.0)
              
              for x in range(len(self.moveVal)):
                dpos[x] -= self.moveVal[x] * .35
                dEndPos[x] -= self.moveVal[x] * .5

            
              self.dash_cloud.setPos(dpos)
                            
              self.dash_cloud.lookAt(self.actor)
              self.dash_cloud.setHpr( (self.dash_cloud.getH() + 90, 0, 0) )

              self.dash_cloud.show()
              self.dash_cloud.setColorScale((1,1,1,1))
              self.dash_cloud.setScale(1)
                
              lerp = Parallel(
                LerpPosInterval(self.dash_cloud, .5, dEndPos),
                LerpColorScaleInterval(self.dash_cloud, .4, (1,1,1,0)),
                LerpScaleInterval(self.dash_cloud, .5, (1.2,1.2,1.2)) 
              )

              lerp.start()
              self.showDashCloud = False

            
            self.isMove[i] = True
          else: 
            self.isMove[i] = False

      pos = self.actor.getPos()

      # ODE Movement
      vel = self.ode_body.getLinearVel()
      force = [0,0,0]

      if abs(vel[0]) < .25 and abs(vel[1]) < .25: self.showDashCloud = True

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

      isTileCol = False

      # Get Dir based on Vel
      x = 0
      y = 0
      if vel[0] > 0: x = 1
      elif vel[0] < 0: x = -1
      else: x = 0

      if vel[1] > 0: y = 1
      elif vel[1] < 0: y = -1
      else: y = 0    
      posDown = (int(tilePos[0]), int(tilePos[1]), int(tilePos[2]) - 1) 

      # Land on Tile
      if posDown in base.tileCoords:
        tile = base.tileCoords[posDown]
        if tile['solid']:

          # Set position to the top of bellow tile
          vel = self.ode_body.getLinearVel()

          if vel[2] < 0:
            self.ode_body.setPosition(pos[0], pos[1], tilePos[2] * 2.0)
            self.shadow_node.setFluidZ( (tilePos[2] * 2.0) - 1.0 )      
            vel[2] = .08       

            # If wasn't previously on the ground show landing cloud object.
            if not self.isOnGround:
            
              # Show Landing Cloud
              dpos = self.actor.getPos()
              dpos[2] -= (self.dimensions[2] * 2.0)

              self.land_cloud.setPos(dpos)
              self.land_cloud.show()
              self.land_cloud.setScale(1)
              self.land_cloud.setTwoSided(True)
              self.land_cloud.setColorScale((1,1,1,1))

              lerp2 = Parallel(
                LerpColorScaleInterval(self.land_cloud, .4, (1,1,1,0)),
                LerpScaleInterval(self.land_cloud, .5, (3,3,3)) 
              )

              lerp2.start()                  

            self.isOnGround = True

      # Side collision
      testPos = self.ode_body.getPosition()
      testPos[0] += (x)
      testPos[1] += (y)

      tilePos = self.getTilePos(testPos)
      posSide = (int(tilePos[0]) , int(tilePos[1]) , int(tilePos[2]))
      if posSide in base.tileCoords:
        tile = base.tileCoords[posSide]
        if tile['solid']:

          vel[0] = -vel[0] * .8
          vel[1] = -vel[1] * .8

          if x: pos[0] = (tile['pos'][0] - x) * 2.0          
          if y: pos[1] = (tile['pos'][1] - y) * 2.0
          self.ode_body.setPosition(pos)
          self.knockback()

          if tile['destructable']:
            self.actions.breakDestructable(tile)

      # Fall off the side
      if pos[2] < -30:
        if not self.isDead:
          lerpMe = LerpColorScaleInterval(self.actor, .5, (1,1,1,0))
          lerpMe.start()

          self.ode_body.setLinearVel( (0,0,0) )

          self.resist = self.maxResist     
          messenger.send("Player_" + str(self.id) + "_Resist_UpdateHud")
          self.noReduce(.75)
          self.moveLock(None, 1.25)

          taskMgr.doMethodLater(.6, self.ode_body.setPosition, "Player_" + str(self.id) + "_FallResetPosition", extraArgs=[self.startPos[0], self.startPos[1], self.startPos[2] + 4], sort=1)
          taskMgr.doMethodLater(.6, self.actor.setColorScale, "Player_" + str(self.id) + "_FallReappear", extraArgs=[(1,1,1,1)], sort=2)
          taskMgr.doMethodLater(.65, self.particlePlay, "Player_" + str(self.id) + "_FallPoof", extraArgs=['diesplosion', 1.5], sort=3)

          # Give the last person to hit a kill.
          if self.lastHit:
            self.lastHit.increaseKillCount()
            self.lastHit = None

        self.isDead = True
        vel[2] = 0
        force[2] = 0
      else:
        self.isDead = False


      # ODE Player Collision
      for i in base.players:
        if i == self: continue
        if i.noCollide == 1 or self.noCollide == 1 or i.noCollide == self or self.noCollide == i: continue

        tPos = i.actor.getPos()
        myPos = self.actor.getPos()

        # If this character collides with another...
        if self.colWithNode(i.actor, i.dimensions):

          # Get the velocities of both characters
          myVel = vel
          eneVel = i.ode_body.getLinearVel()

          # Determine how power and resist should affect this collision
          myPower = self.power - (i.resist)
          enePower = i.power - (self.resist)

          # Set velocities.
          for x in range(2):
            myVel[x] += myPower * self.moveVal[x]
            eneVel[x] += enePower * i.moveVal[x]

          # Move Special
          if self.moveSpecial:
            eneVel = Vec3(0,0,0)
          
          if i.moveSpecial:
            myVel = Vec3(0,0,0)


          vel = eneVel
          i.ode_body.setLinearVel(VBase3(myVel[0], myVel[1], myVel[2]) )

          # Reduce Reduce
          if abs(myVel[0]) > 5.0 or abs(myVel[1]) > 5.0:
            i.reduceResist()
            i.lastHit = self

          if abs(eneVel[0]) > 5.0 or abs(eneVel[1]) > 5.0:
            self.reduceResist()
            self.lastHit = i

          # Sound FX
          self.sfx['bump'].play()

          # Particle FX
          self.particlePlay('stars', .15)

          # Knockback
          self.knockback()
          i.knockback()   

          # Drop object
          self.actions.drop()
          i.actions.drop()             

          # Flag characters to not accept collisions from each other for the next .5 seconds
          self.setNoCollide(.5, i)
          i.setNoCollide(.5, self)

      if not isTileCol:
        self.noTilePos = self.getTilePos()        

      # ODE Step

      self.ode_body.setLinearVel(vel[0], vel[1], vel[2])
      self.ode_body.setForce(force[0], force[1], force[2])

      odePos = self.ode_body.getPosition()
      odePos[2] += self.zOffset
      self.actor.setFluidPos(render, odePos)

      # Set Rotation [Direction]

      if not self.isKnockback and not self.isMove == [False, False]:
        self.direction = [self.moveVal[0], self.moveVal[1]]

      pos = self.actor.getPos()
      self.actor.lookAt( (pos[0] + self.direction[0], pos[1] + self.direction[1], pos[2]) )
      self.actor.setH(self.actor.getH() - 180)     

      # Animations

      # Falling
      if vel[2] <= -.75 and pos[2] < -.5:
        self.setAnim("fall", True)

      # If moving because of a special ability.
      elif (vel[0] or vel[1]) and self.moveSpecial:
        self.setAnim("special", True)

        self.actor.lookAt( (pos[0] + self.direction[0], pos[1] + self.direction[1], pos[2]) )
        self.actor.setH(self.actor.getH() - 180)          

      # If knocked back by another force...
      elif self.isKnockback:
        self.setAnim("bump", True)
      
      # If moved by player the animation
      elif self.isMove[0] or self.isMove[1]:
      
        # Animation speed...
        speed = vel[0]
        if abs(vel[1]) > abs(vel[0]): speed = vel[1]
        speed = abs(speed / self.moveSpeed)
        if speed < .5: speed = .5
        self.actor.setPlayRate( .5 + speed, self.animMove)
        
        self.setAnim(self.animMove, True)
            
      # Otherwise play default animation.
      else:
        self.setAnim(self.animDefault, True)
  

      # Shadow Node
      self.shadow_node.setFluidX(self.actor.getX())
      self.shadow_node.setFluidY(self.actor.getY())

      azPos = self.actor.getZ()
      szPos = self.shadow_node.getZ()


      posDelta = (azPos - self.zOffset) - szPos
      if posDelta >= self.dimensions[2]:
        self.shadow_node.show()
        self.shadow_node.setScale(.5 / (abs(posDelta) ))
      else:
        self.shadow_node.hide()
      

      task.lastTime = task.time
      
    return task.cont


  def knockback(self, task = None):

    """
    To use after a knockback. Restores controls of player
    once the players comes to a stop.
    """

    if not task:
      taskMgr.add(self.knockback, "Player_" + str(self.id) + "_Knockback")
      return None    

    vel = self.ode_body.getLinearVel()

    if (abs(vel[0]) < 2.0 and abs(vel[1]) < 2.0) or task.time > .75:
      self.isKnockback = False
      self.moveSpecial = False
      taskMgr.remove("Player_" + str(self.id) + "_MoveLock")
      self.doMovementLock = False
      return task.done
    self.isKnockback = True
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
      pos[i] = int(math.floor( (pos[i] + self.dimensions[i]) / 2.0))
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

  def setAnim(self, name, loop, startFrom = 0, endAt = None):

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
      self.actor.play(name, fromFrame = startFrom, toFrame = endAt)
      self.isPlaying = True
      self.animation = name
      taskMgr.remove("Player_" + str(self.id) + "_AnimationDoneCheck")
      taskMgr.add(self.getAnimDone, "Player_" + str(self.id) + "_AnimationDoneCheck")
      return True

    # For loops... if animation is already set then no need to restart it.
    #if self.animation == name: return None
    
    self.loopAnimation = name

    # Play loop as long as there is no one time animations playing.

    if not self.isPlaying:
      self.animation = name
      self.actor.loop(self.animation, restart = 0, fromFrame = self.animConfig[name]['loopfrom'], toFrame = self.animConfig[name]['loopto'] )
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

  def reduceResist(self, ammt = .5):

    """
    Reduce resistance after getting bumped.
    """

    if not self.isNoReduce:
      self.resist -= ammt
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

    # Bot Break Free
    if taskMgr.hasTaskNamed("Player_" + str(self.id) + "_AI"):
      taskMgr.doMethodLater(self.breakFreeCt * .25, self.heldBy.actions.drop, "Player_" + str(self.id) + "_AIBreakFree", extraArgs=[1.0])

    # Player break free
    else:
      moveKeys = [[1,0], [-1,0]]

      # To break free player must press the direction keys in a sequence...
      if self.kbVal == moveKeys[self.breakFreeCt % 2]:
        self.breakFreeCt -= 1
        if self.breakFreeCt <= 0:
          self.heldBy.actions.drop(1.0)
          return task.done

      if taskMgr.getTasksMatching("Player_" + str(self.id) + "_MoveLoop"):
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
    self.direction = [self.moveVal[0], self.moveVal[1]]

    if not canControl:
      self.knockback()
      self.moveLock(None, 9999)
      self.isKnockback = True
      
    # Play Sound
    if movement > 10:
      self.sfx['lunge'].play()

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


  def particlePlay(self, name, time, doReturn = False):

    """
    Play a particle effect for a period of time.
    """
    p = ParticleEffect()
    p.loadConfig(base.assetPath + "/particles/" + name + ".ptf")
    p.start(self.actor, render)
    taskMgr.doMethodLater(time, p.softStop, "Player_" + str(self.id) + "_StarsParticleStop", extraArgs=[])
    taskMgr.doMethodLater(time * 2.5, p.cleanup, "Player_" + str(self.id) + "_StarsParticleCleanup", extraArgs=[])    

    if doReturn:
      return p

  def increaseKillCount(self):

    """
    Increase player kill counter, show indication.
    """

    self.killCount += 1
    self.getKill.show()
    self.killLerp.start()

  def networkPosition(self, task = None):

    pos = self.actor.getPos()
    h = self.actor.getH()
    messenger.send("network-send", ["position", chr(int(self.controls)) + str(pos[0]) + "x" + str(pos[1]) + "x" + str(pos[2]) + "x" + str(h)])

    if task:
      return task.again

  def destroy(self):

    taskMgr.removeTasksMatching("Player_" + str(self.id) + "*")
    if self.local: base.gameCam.remove(self)
    base.players.remove(self)
    self.actor.cleanup()
    self.actor.removeNode()
    self.shadow_node.removeNode()
