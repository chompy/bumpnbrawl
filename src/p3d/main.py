# Import Panda3D Modules
from pandac.PandaModules import loadPrcFileData, VBase4, AntialiasAttrib, TextNode, OdeWorld, OdeSimpleSpace, OdeJointGroup, PointLight, Spotlight, PerspectiveLens, Vec4, AmbientLight
from panda3d.core import loadPrcFile
from direct.gui.OnscreenText import OnscreenText

# Import game specific modules
import mapLoader, player, camera, hud, gameInput, network

# Config
loadPrcFile("../../assets/Config.prc")

# ShowBase
import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase

# Antialiasing
render.setAntialias(AntialiasAttrib.MAuto)

# Path to game assets.
base.assetPath = "../../assets"

# Ext to use when loading tiles.
base.tileExt = "egg"

# Ext to use when loading character.
base.charExt = "egg"

# Special Ability Cooldown Time
base.sa_cooldown = 7.5

# Setup ODE
base.ode_world = OdeWorld()
base.ode_world.setGravity(0, 0, -9.81)

deltaTimeAccumulator = 0.0
stepSize = 1.0 / 90.0

# Make Background Color Black
base.win.setClearColorActive(True)
base.win.setClearColor(VBase4(0, 0, 0, 1))

# Enable Particle System
base.enableParticles()

# Controls

CONTROL1 = {
  'left'    :   'arrow_left',
  'right'   :   'arrow_right',
  'up'      :   'arrow_up',
  'down'    :   'arrow_down',
  'btn1'    :   'shift',
  'btn2'    :   'z'
}

CONTROL2 = {
  'left'    :   'a',
  'right'   :   'd',
  'up'      :   'w',
  'down'    :   's',
  'btn1'    :   'q',
  'btn2'    :   'e'
}

class ChompinBomper(ShowBase):

  def __init__(self):

    """
    Init ze game!
    """

    # Game Input
    self.input = gameInput.gameInput()

    # Load Map
    self.map = mapLoader.mapLoader(base.assetPath + "/maps/chomp_map2.png")

    # Load Players
    base.playerid = 0
    base.players = []
    base.players.append(player.player("chompy", True, 2))
    #base.players.append(player.player("chompy", True, 2))
    #base.players.append(player.player("chompy", False))
    #base.players.append(player.player("chompy", False))   

    # Load Camera
    base.gameCam = camera.camera(base.players[0])
    #base.gameCam.add(base.players[1])

    # Game Hud
    self.hud = hud.gameHud()

    # Window Event
    self.accept(base.win.getWindowEvent(), self.windowEvent)
    self.windowEvent()

    # Debug Text Area
    self.debug = OnscreenText(text = '<DEBUG>', fg=(1,1,1,1), pos = (-self.winAspect + .1, .8), scale = 0.05, align=TextNode.ALeft)
    self.debug.hide()

    # ODE Loop
    taskMgr.add(self.odeStep, "ODE_Step", sort=1)

    # Activate Debugging
    # taskMgr.add(self.showDebug, "Debugger")

    #slight = Spotlight('slight')
    #slight.setColor(VBase4(1, 1, 1, 1))
    #lens = PerspectiveLens()
    #slight.setLens(lens)
    #slight.setShadowCaster(True, 512, 512)
    #slnp = render.attachNewNode(slight)
    #slnp.setPos(self.map.mapSize[0] / 2.0, -self.map.mapSize[1] / 1.15, 15)
    
    #slnp.setP(-15)
    #render.setLight(slnp)

    #alight = AmbientLight('alight')
    #alight.setColor(VBase4(1, 1, 1, 1))
    #alnp = render.attachNewNode(alight)
    #render.setLight(alnp)

    #render.setShaderAuto()
    run()

  def showDebug(self, task = None):    

    self.debug.show()
    ct = 1
    debugStr = ""
    for i in base.players:
      dbLine = "PLAYER " + str(ct) + "\n POS: " + str(i.actor.getPos()) + " DIR: " + str(i.direction)
      dbLine += " SPECIAL " + str(i.moveSpecial) + " MOVEVAL " + str(i.moveVal)
      debugStr += dbLine + "\n"
      ct += 1
    self.debug.setText(debugStr)
    
    if task: return task.cont
  def windowEvent(self, window = None):

    """
    Update window size info everytime a window event occurs.
    """

    self.winWidth = base.win.getProperties().getXSize() 
    self.winHeight = base.win.getProperties().getYSize()
    self.winAspect = float(self.winWidth) / float(self.winHeight)

  def odeStep(self, task):

    global deltaTimeAccumulator 
    deltaTimeAccumulator += globalClock.getDt()
    while deltaTimeAccumulator > stepSize:
      deltaTimeAccumulator -= stepSize
  
      base.ode_world.quickStep(stepSize)

    return task.cont

    

ChompinBomper()
