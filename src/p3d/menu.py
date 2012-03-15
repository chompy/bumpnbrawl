# Import Panda3D Modules
import sys
from pandac.PandaModules import loadPrcFileData, TextNode, NodePath, CardMaker,TextureStage, Texture, VBase3, TransparencyAttrib
from direct.interval.LerpInterval import LerpHprInterval
from panda3d.core import loadPrcFile
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.fsm.FSM import FSM
from direct.interval.LerpInterval import LerpColorScaleInterval, LerpPosHprScaleInterval
from direct.interval.MetaInterval import Sequence

from lib import menuBars, menuOptions
import gameInput

# Config
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

class mainMenu(FSM):

  def __init__(self):

    # Init FSM
    FSM.__init__(self, 'MenuFSM')

    # Disable Mouse
    base.disableMouse()

    # Game Input
    self.input = gameInput.gameInput()

    # Menu node
    self.node = NodePath("MenuNode")
    self.node.reparentTo(render)

    self.windowObj = []

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

    # Menu Bar
    self.menuBar = menuBars.menuBars([])
    self.menuBar.node.setZ(.7)
    self.addWindowNode(self.menuBar.node, -1, .3)

    # Menu Options
    self.menuOptions = menuOptions.menuOptions([])
    self.menuOptions.node.setZ(.7)
    self.addWindowNode(self.menuOptions.node, -1, .8)

    # Bind Window Event
    self.windowEvent()  
    self.accept("window-event", self.windowEvent)    

    # Get Window resolutions available
    di = base.pipe.getDisplayInformation()
    self.resolutions = []

    for index in range(di.getTotalDisplayModes()):
      addSize = True
      for i in self.resolutions:
        if i == [di.getDisplayModeWidth(index), di.getDisplayModeHeight(index)]:
          addSize = False
          break
      if addSize:
        self.resolutions.append( [di.getDisplayModeWidth(index), di.getDisplayModeHeight(index)] )

  def enterTitle(self):

    """
    Enter title screen menu.
    """

    self.titleNode.show()
    self.accept("p1_btna", self.request, ['Main'])
    self.accept("mouse1", self.request, ['Main'])

  def exitTitle(self):

    """
    Exit title screen menu.
    """

    logoLerp = LerpPosHprScaleInterval(
      self.logo, 
      .75,
      (self.winAspect - .7,0,.3), 
      (0,0,0), 
      .8)

    logoLerp.start()

    self.addWindowNode(self.logo, 1, -.7)

    #taskMgr.doMethodLater(2.25, self.titleNode.hide, "MenuHideTitle", extraArgs=[])


    self.ignore("p1_btna")
    self.ignore("mouse1")

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

  def exitMain(self):

    """
    Exit main menu.
    """

    self.mainNode.hide()

  def enterOptions(self):

    OPTIONS = [
      ['Back', self.request, ['Main']]
    ]

    self.menuBar.setOptions(OPTIONS)

    MO_OPTIONS = [

      ['Resolution',  [],
        len(self.resolutions) - 1
      ],

      ['Window Mode', [
        ['Windowed', None, [0]],
        ['Fullscreen', None, [1]]
        
      ], 0],

      ['Config Controls', [
        ['go...', None, [0]],        
      ]]      

    ]

    # Add resolutions
    for i in self.resolutions:
      MO_OPTIONS[0][1].append([str(i[0]) + "x" + str(i[1]), self.setRes, [i[0], i[1]]])

    self.menuOptions.setOptions(MO_OPTIONS)

    # Add player input back button
    self.accept("p1_btnb", self.request, ['Main'])

  def exitOptions(self):

    self.menuOptions.setOptions([])

  def setRes(self, x, y):
    print "RESOLUTION SET: " + str(x) + "x" + str(y)
    
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
