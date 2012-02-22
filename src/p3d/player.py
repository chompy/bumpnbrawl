from direct.actor.Actor import Actor
from lib import basePolling
import math,random, os, actions, ConfigParser

GRAVITY = .5

class player:

  def __init__(self, character = "cuby", local=True, controls = False):
 
    """
    Init a player character.
    """

    # Set ID
    base.playerid += 1
    self.id = base.playerid

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

    # Vars
    self.moveVal = [0,0]
    self.movement = [0,0]
    self.collision = [0,0]
    self.isMove = [False, False]
    self.tilePos = (0,0,0)
    self.fallrate = 0
    self.isKnockback = False
    self.direction = [0,1]
    self.isHeld = False
    self.reverseGravity = 0.0
    self.noCollide = None
    self.animation = ""
    self.loopAnimation = ""
    self.isPlaying = False
    self.animDefault = "idle"
    self.animMove = "run"

    # Set Start Position
    self.startPos = base.playerStart[self.id - 1]
    self.actor.setPos(self.startPos)

    # Stats
    self.accelerate = 15.0
    self.moveSpeed = 5.0
    self.power = 15.0
    self.resist = 10.0

    # Keyboard Interface
    self.local = local
    if local:
      self.controls = controls

    # Setup Action module
    self.actions = actions.actions(self)
    if local:
      base.accept(self.controls['btn1'], self.actions.pickup)
      base.accept(self.controls['btn2'], self.actions.punch)
    
    self.i = basePolling.Interface()

    taskMgr.add(self.moveLoop, "Player_" + str(self.id) + "_MoveLoop")   
    taskMgr.add(self.fallLoop, "Player_" + str(self.id) + "_FallLoop")

    # Begin Animation
    self.setAnim(self.animDefault, True)
    
  def move(self, val):

    """
    Prepares the character to be moved.
    """

    for i in range(len(val)):
      if type(val[i]) == int:
        self.moveVal[i] = val[i]
        self.isMove[i] = True

    for i in range(len(self.moveVal)):
      if self.moveVal[i] == 0:
        self.isMove[i] = False

  def moveLoop(self, task):

    """
    Moves the character.
    """

    try:
      task.lastTime
    except:
      task.lastTime = 0

    dt = task.time - task.lastTime

    # Poll for key presses.
    if self.local:
      if self.i.getButton(self.controls['up']): 
        if self.movement[1] < 0:
          self.isMove[1] = False
        else:
          self.moveVal[1] = 1
          self.isMove[1] = True

      elif self.i.getButton(self.controls['down']): 
        
        if self.movement[1] > 0:
          self.isMove[1] = False
        else:
          self.moveVal[1] = -1
          self.isMove[1] = True

      else:
        self.isMove[1] = False

      if self.i.getButton(self.controls['right']): 

        if self.movement[0] < 0:
          self.isMove[0] = False
        else:
          self.isMove[0] = True
          self.moveVal[0] = 1

      elif self.i.getButton(self.controls['left']): 

        if self.movement[0] > 0:
          self.isMove[0] = False
        else:
          self.isMove[0] = True
          self.moveVal[0] = -1

      else: 
        self.isMove[0] = False

    for i in range(len(self.moveVal)):

      # Acceleration
      if self.isMove[i]:
        if abs(self.movement[i]) < abs(self.moveSpeed):
          self.movement[i] += (self.accelerate * self.moveVal[i]) * dt
        else:
          self.movement[i] = self.moveSpeed * self.moveVal[i]

      # Deceleration
      else:
        if self.movement[i] * self.moveVal[i] > 0:
          self.movement[i] -= (self.accelerate * self.moveVal[i]) * dt

        # If all movements have reached 0 then we're done.
        else:
          self.movement[i] = 0
          self.isMove[i] = False
          self.moveVal[i] = 0

    # Set Rotation
    if not self.isKnockback and not self.isMove == [False, False]:
      if self.moveVal == [1,0]:
        self.actor.setHpr(90,0,0)
        self.direction = [1,0]
        
      elif self.moveVal == [-1,0]:
        self.actor.setHpr(270,0,0)
        self.direction = [-1,0]
        
      elif self.moveVal == [0,1]:
        self.actor.setHpr(180,0,0)
        self.direction = [0,1]

      elif self.moveVal == [0,-1]:
        self.actor.setHpr(0,0,0)
        self.direction = [0,-1]
        
      elif self.moveVal == [1,1]:
        self.actor.setHpr(135,0,0)
        self.direction = [1,1]
        
      elif self.moveVal == [1,-1]:
        self.actor.setHpr(45,0,0)
        self.direction = [1,-1]
        
      elif self.moveVal == [-1,-1]:
        self.actor.setHpr(315,0,0)
        self.direction = [-1,-1]
        
      elif self.moveVal == [-1,1]:
        self.actor.setHpr(225,0,0)  
        self.direction = [-1,1]

    # Get Posision.
    pos = self.actor.getPos()

    # Detect Collisions with tiles
    hasCollision = False
    for x in base.tilePositions:
      tilePos = x['pos'] * 2.0
      if not x['solid']: continue
      #if not tilePos[2] == pos[2]: continue
      if x['id'] == 1: continue

      ct = 0
      while (self.colWithTile(tilePos) and ct < 200):
        for i in range(len(self.direction)):
          pos[i] -= self.moveVal[i] * 0.01
        self.actor.setFluidPos(pos)       
        ct += 1

    # Check for collision with players
    if not self.isKnockback:
      for i in base.players:
        if i == self: continue
        if i == self.noCollide: continue
        if not i.actor.getZ() == pos[2]: continue
        if self.colWithNode(i.actor):

          if i.moveVal == [0,0] and self.moveVal == [0,0]:
            # Push players off of each other
            ct = 0
            while (self.colWithNode(i.actor) and ct < 200):
              for x in range(len(self.direction)):
                pos[x] += self.moveVal[x] * 0.01
              self.actor.setFluidPos(pos)       
              ct += 1            
            pos[x] += self.moveVal[x] * 0.4
            self.actor.setFluidPos(pos)              

          else:
            # Reverse Movement and swap momentum with other player.
            for x in range(len(self.moveVal)):
              pos[x] -= .4 * self.moveVal[x]
            
            for x in range(len(self.moveVal)):
              pmoveVal = self.moveVal[x]
              pmovement = self.movement[x]
            
              self.moveVal[x] = i.moveVal[x] * 1.5
              self.movement[x] = i.movement[x] * 1.5

              i.moveVal[x] = pmoveVal * 1.5
              i.movement[x] = pmovement * 1.5
              
              self.isMove[x] = False
              i.isMove[x] = False

            if self.local:
              self.local = False
              self.isKnockback = True
              taskMgr.add(self.knockback, "Player_" + str(self.id) + "Knockback")

            if i.local:
              i.local = False
              i.isKnockback = True
              taskMgr.add(i.knockback, "Player_" + str(i.id) + "Knockback")

            # Drop Picked up Object
            if self.actions.pickupObj:
              self.actions.drop()            
                 
    # Update Position
    if not hasCollision:
      pos[0] += self.movement[0] * dt
      pos[1] += self.movement[1] * dt

    # Animations

    # Falling
    if self.fallrate > 0.0:
      self.setAnim("fall", True)
    
    # If moved by player the animation
    elif self.isMove[0] or self.isMove[1]:
      self.setAnim(self.animMove, True)
          
    # If knocked back by another force...
    elif (self.moveVal[0] or self.moveVal[1]) and not self.moveVal == self.direction:
      self.setAnim("bump", True)

    # Otherwise play default animation.
    else:
      self.setAnim(self.animDefault, True)

    self.actor.setFluidPos(pos)    

    task.lastTime = task.time
    return task.cont

  def fallLoop(self, task):

    """
    Causes player to fall when not on a tile.
    """

    # Get Deltatime
    try:
      task.lastTime
    except:
      task.lastTime = 0

    dt = task.time - task.lastTime

    if not self.isHeld:
      # Check tile below player
      tilePos = self.getTilePos()
      tilePos[2] -= 1

      # Determine if there is a tile or not
      falling = True
      for x in base.tilePositions:
        if x['pos'] == tilePos and x['solid']:
          falling = False
          self.actor.setFluidZ(x['pos'][2])          
          break

      # Determine if there is a player
      tilePos[2] += 1
      for x in base.players:
        if x == self: continue
        if x.isHeld: continue
        if x.getTilePos() == tilePos:
          pos = x.getTilePos()
          for y in range(len(x.direction)):
            pos[y] -= x.direction[y]
          x.actor.setFluidPos(pos * 2.0)

      if falling and self.fallrate <= 0.0: self.fallrate = .001
      elif not falling: self.fallrate = 0.0

      if self.fallrate > 0.0:
        self.fallrate = self.fallrate * 1.7
        if self.fallrate > abs(GRAVITY): self.fallrate = abs(GRAVITY)
        pos = self.actor.getPos()
        if self.reverseGravity > 0.0:
          pos[2] += self.fallrate
          self.reverseGravity -= .075 * self.fallrate
        else:
          pos[2] -= self.fallrate
        self.actor.setFluidPos(pos)
    else:
      falling = False

    # Reset Position
    if not falling and self.actor.getZ() < 0.0:
      self.actor.setZ(0.0)
      
    if self.actor.getZ() < -10:
      self.actor.setPos(self.startPos)
      self.actor.setZ(10)
      self.resetNoCollide()

    if self.i.getButton("f1"):
      self.fallrate = 0.0
      self.actor.setFluidZ(10)

    return task.cont

  def knockback(self, task):

    """
    To use after a knockback. Restores controls of player
    once the players comes to a stop.
    """

    if self.moveVal == [0,0]:
      self.local = True
      self.isKnockback = False
      return task.done
    self.isKnockback = True
    return task.cont

  def moveLock(self, task):

    """
    Unlocks movement.
    """

    self.local = True
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

  def colWithBox(self, pos, dimensions):

    """
    Check to see if there is a rect collision with a box.
    """

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

  def resetNoCollide(self, task = None):

    """
    Reset player no collide flag.
    """

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
    
