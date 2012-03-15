# Import Panda3D Modules
import sys, os
from pandac.PandaModules import loadPrcFileData, TextNode, NodePath, CardMaker,TextureStage, Texture, VBase3, TransparencyAttrib, WindowProperties, TextProperties, TextPropertiesManager
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpHprInterval
from panda3d.core import loadPrcFile
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.fsm.FSM import FSM
from direct.interval.LerpInterval import LerpColorScaleInterval, LerpPosHprScaleInterval, LerpHprInterval
from direct.interval.MetaInterval import Sequence

from lib import menuBars, menuOptions, inputHelp
import gameInput

loadPrcFile("../../assets/Config.prc")

# ShowBase
import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase

# Path to game assets.
base.assetPath = "../../assets"

# Ext to use when loading tiles.
base.tileExt = "egg"

# Ext to use when loading character.
base.charExt = "egg"

# Get Display Resolution

# Windows
try:
  import ctypes
  user32 = ctypes.windll.user32
  screensize = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
except:

  # Linux
  try:
    screensize = os.system("xrandr  | grep \* | cut -d' ' -f4").split("x")
  except:
    screensize = [640,480]
  

class mainMenu(FSM):

  def __init__(self):

    # Init FSM
    FSM.__init__(self, 'MenuFSM')

    # Disable Mouse
    base.disableMouse()

    # Load Fonts
    self.boldFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansBold.ttf")
    self.regFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansCondensed.ttf")

    # Game Input
    self.input = gameInput.gameInput()

    # Input Help
    self.inputHelp = inputHelp.inputHelp([])

    # Menu node
    self.node = NodePath("MenuNode")
    self.node.reparentTo(render)

    self.windowObj = []

    # Set Text Properites
    tpMgr = TextPropertiesManager.getGlobalPtr()

    # Bold
    tpBold = TextProperties()
    tpBold.setFont(self.boldFont)
    tpMgr.setProperties("bold", tpBold)
        

    # Prepare menu BG
    menu_frame = CardMaker("Menu_Background")
    menu_frame.setFrame(-4,4,-4,4)
    menu_frame.setColor(0.3843137254901961, 0.8509803921568627, 0.6117647058823529,1)
    menu_frame_node = self.node.attachNewNode(menu_frame.generate())
    menu_frame_node.setY(8)
    

    bgTex = loader.loadTexture(base.assetPath + "/menu/bg_overlay.png")

    bgTex.setWrapU(Texture.WMRepeat)
    bgTex.setWrapV(Texture.WMRepeat)

    #menu_frame_node.setTexture(bgTex)

    ts = TextureStage('PlayerHud_Snapshot_TextureStage')
    ts.setMode(TextureStage.MDecal)
    menu_frame_node.setTexture(ts, bgTex)    

    lerper = NodePath("Menu_Background_Lerper")
    menu_frame_node.setTexProjector(ts, NodePath(), lerper)
    menu_lerp = lerper.posInterval(60, VBase3(-1, 1, 0))
    menu_lerp.loop()

    # TITLE SCREEN ASSETS
    # ===================

    self.titleNode = NodePath("MenuTitle")
    self.titleNode.reparentTo(aspect2d)
    self.titleNode.hide()

    # Logo
    self.logo = OnscreenImage(image = base.assetPath + "/menu/logo.png", pos = (-0.0, 0, 0.0), parent=self.titleNode)
    self.logo.setTransparency(TransparencyAttrib.MAlpha)

    # Press ? To Start Text

    self.startText = OnscreenText(
        text = "Click or Press \1bold\1" + self.inputHelp.getEventKey("p1_btna") + "\2 to start!",
        fg=(1,1,1,1), 
        shadow=(0,0,0,.6),
        align=TextNode.ACenter, 
        font=self.regFont, 
        pos = (0, -.85), 
        scale = 0.06, 
        parent=aspect2d
        )

    self.sTextLerp = LerpColorScaleInterval(self.startText, .5, (1,1,1,0))    

    # MENU ASSETS
    # ===================

    # Menu Bar
    self.menuBar = menuBars.menuBars([])
    self.menuBar.node.setZ(.7)
    self.addWindowNode(self.menuBar.node, -1, .3)

    # Menu Options
    self.menuOptions = menuOptions.menuOptions([])
    self.menuOptions.node.setZ(.7)
    self.addWindowNode(self.menuOptions.node, -1, .8)

    # Random Background Character
    character = "chompy"
    self.randChar = Actor(base.assetPath + "/characters/" + character + "/model." + base.charExt,
      {'default' : base.assetPath + "/characters/" + character + "/model-idle." + base.charExt }
    )
    self.randChar.reparentTo(self.node)
    self.randChar.setY(5)
    self.addWindowNode(self.randChar, -1, 1.2)
    self.randChar.setScale(.4)
    self.randChar.loop("default")
    lerp = LerpHprInterval(self.randChar, 18.0, (359,0,0), (0,0,0))
    lerp.loop()

    # Bind Window Event
    self.windowEvent()  
    self.accept("window-event", self.windowEvent)    

    # Option Vars
    self.windowMode = False

    self.addWindowNode(self.inputHelp.node, -1, .1)
    self.inputHelp.node.setZ(-.9)

  def enterTitle(self):

    """
    Enter title screen menu.
    """

    self.titleNode.show()
    base.accept("p1_btna", self.request, ['Main'])
    base.accept("mouse1", self.request, ['Main'])

  def exitTitle(self):

    """
    Exit title screen menu.
    """

    # Move the logo to the top right.
    logoLerp = LerpPosHprScaleInterval(
      self.logo, 
      .75,
      (self.winAspect - .7,0,.3), 
      (0,0,0), 
      .8)

    logoLerp.start()
    self.addWindowNode(self.logo, 1, -.7)

    # Fade on the 'Press ? To Start' text
    self.sTextLerp.start()

    # Ignore the Start Buttons
    base.ignore("p1_btna")
    base.ignore("mouse1")

  def enterMain(self):

    """
    Enter main menu.
    """

    self.mainNode = NodePath("MenuMain")
    self.mainNode.reparentTo(aspect2d)

    OPTIONS = [
      ['Online', self.request, ['Online']],
      ['Local', self.request, ['Local']],
      ['Options', self.request, ['Options']],
      ['Quit', sys.exit, []]
    ]

    self.menuBar.setOptions(OPTIONS)

    # Input Help Options
    self.inputHelp.setOptions([
      ['Confirm', 'p1_btna']    
    ])    

    base.ignore("p1_btnb")

  def exitMain(self):

    """
    Exit main menu.
    """

    self.mainNode.hide()

  def enterOptions(self):

    OPTIONS = [
      ['Back', self.request, ['Main']]
    ]

    self.menuBar.setOptions(OPTIONS, False)

    MO_OPTIONS = [


      ['Window Mode', [
        ['Windowed', self.setWindowMode, [False]],
        ['Borderless-Full', self.setWindowMode, [True]]
        
      ], self.windowMode],

      ['Player Controls', [
        ['Configure...', self.request, ['ControlConfigSelect']],        
      ]]      

    ]

    self.menuOptions.setOptions(MO_OPTIONS)

    # Add player input back button
    base.accept("p1_btnb", self.request, ['Main'])

    # Input Help Options
    self.inputHelp.setOptions([
      ['Enter Submenu', 'p1_btna'],
      ['Back', 'p1_btnb']    
    ])

  def exitOptions(self):

    self.menuOptions.setOptions([])

    # Set Window Properties
    wp = WindowProperties.getDefault() 
    if self.windowMode:
      wp.setSize(screensize[0], screensize[1]) 
      wp.setOrigin(0,0) 

    wp.setUndecorated(self.windowMode) 
    base.win.requestProperties(wp) 

    # Input Help Options
    self.inputHelp.setOptions([])

    base.ignore("p1_left")
    base.ignore("p1_right")      
    base.ignore("p1_up")      
    base.ignore("p1_down")
    base.ignore("p1_btna")      
    base.ignore("p1_btnb")    

  def enterControlConfigSelect(self):

    """
    Enter menu for configuring player controls.
    """
    OPTIONS = [
      ['Back', self.request, ['Options']]
    ]

    self.menuBar.setOptions(OPTIONS, False)

    MO_OPTIONS = [

      ['Player 1 Controls', [
        ['Configure...', self.request, ['ConfigControl', '1']],
      ]],      

      ['Player 2 Controls', [
        ['Configure...', self.request, ['ConfigControl', '2']],
      ]],     

      ['Player 3 Controls', [
        ['Configure...', self.request, ['ConfigControl', '3']],
      ]],     

      ['Player 4 Controls', [
        ['Configure...', self.request, ['ConfigControl', '4']],        
      ]]      

    ]

    self.menuOptions.setOptions(MO_OPTIONS)

    # Add player input back button
    base.accept("p1_btnb", self.request, ['Options'])

    # Input Help Options
    self.inputHelp.setOptions([
      ['Configure Control', 'p1_btna'],
      ['Back', 'p1_btnb']
    ])    


  def enterConfigControl(self, player):

    """
    Config controls for a player.
    """

    # Bar Options
    OPTIONS = [
      ['Back', self.request, ['ControlConfigSelect']]
    ]

    # Config Options
    self.menuBar.setOptions(OPTIONS, False)

    self.configKeys = {
      0 : 'p' + str(player) + '_up',
      1 : 'p' + str(player) + '_right',      
      2 : 'p' + str(player) + '_down',
      3 : 'p' + str(player) + '_left',
      4 : 'p' + str(player) + '_btna',
      5 : 'p' + str(player) + '_btnb'

    }

    MO_OPTIONS = [

      ['Player '+str(player)+' Up', [
        [self.inputHelp.getEventKey('p' + str(player) + '_up'), self.defineInput, [player, 0]],
      ]],      

      ['Player '+str(player)+' Right', [
        [self.inputHelp.getEventKey('p' + str(player) + '_right'), self.defineInput, [player, 1]],
      ]],      

      ['Player '+str(player)+' Down', [
        [self.inputHelp.getEventKey('p' + str(player) + '_down'), self.defineInput, [player, 2]],
      ]],      

      ['Player '+str(player)+' Left', [
        [self.inputHelp.getEventKey('p' + str(player) + '_left'), self.defineInput, [player, 3]],
      ]],

      ['Player '+str(player)+' Button A', [
        [self.inputHelp.getEventKey('p' + str(player) + '_btna'), self.defineInput, [player, 4]],
      ]],              

      ['Player '+str(player)+' Button B', [
        [self.inputHelp.getEventKey('p' + str(player) + '_btnb'), self.defineInput, [player, 5]],
      ]],              

    ]
    
    self.menuOptions.setOptions(MO_OPTIONS)

    # Input Help Options
    self.inputHelp.setOptions([
      ['Define Input', 'p1_btna'],
      ['Back', 'p1_btnb']
    ])            

    # Add player input back button
    base.accept("p1_btnb", self.request, ['ControlConfigSelect'])    

  def defineInput(self, playerNo, inputDefine):

    """
    Define input for player controls.
    """

    self.menuOptions.optionNodes[inputDefine][2]['text'] = "...press key..."
    base.ignore("p1_left")
    base.ignore("p1_right")      
    base.ignore("p1_up")      
    base.ignore("p1_down")
    base.ignore("p1_btna")      
    base.ignore("p1_btnb")
    self.input.pollKeys()
    taskMgr.doMethodLater(.2, base.accept, "MenuDelayConfigKeyPress", ["keyPoll", self.getInput, [playerNo, inputDefine]])

  def getInput(self, playerNo, inputDefine, key):

    """
    Accepts any key input and binds it to a player.
    """

    # Stop Polling
    base.ignore("keyPoll")
    self.input.stopPollKeys()
    

    # Check if key is already in use.
    for x in base.controls[playerNo]:
      if base.controls[playerNo][x] == key:
        self.menuOptions.optionNodes[inputDefine][2]['text'] = "..already in use.."
        taskMgr.doMethodLater(1, self.defineInput, "MenuKeyConfigInUse", [playerNo, inputDefine])
        return None

    # Save to conf file.
    if not key == "escape": 
      self.input.setKey(self.configKeys[inputDefine], key)
    self.menuOptions.activateKeyboard()
    self.menuOptions.optionNodes[inputDefine][2]['text'] = self.inputHelp.getEventKey(self.configKeys[inputDefine])

    # Add player input back button
    base.accept("p1_btnb", self.request, ['ControlConfigSelect'])    
    

  def setWindowMode(self, isFullscreen):

    self.windowMode = isFullscreen
    
    
  def addWindowNode(self, node, side, xoffset):

    """
    Add NodePath to list of nodes that will be
    repositioned everytime the window is resized.
    """
     
    self.windowObj.append([node, side, xoffset])

  def rmWindowNode(self, node):

    """
    Remove NodePath from above list.
    """

    for i in self.windowObj:
      if i[0] == node:
        self.windowObj.remove(i)
        break

  def windowEvent(self, window = None):

    """
    Update window size info everytime a window event occurs.
    """

    self.winWidth = base.win.getProperties().getXSize() 
    self.winHeight = base.win.getProperties().getYSize()
    self.winAspect = float(self.winWidth) / float(self.winHeight)  

    # Update Node
    for i in self.windowObj:
      i[0].setX((self.winAspect * i[1]) + i[2])

m = mainMenu()
m.request("Title")
run()
