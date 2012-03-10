# Import Panda3D Modules
from pandac.PandaModules import loadPrcFileData, TextNode, NodePath, CardMaker,TextureStage, Texture, VBase3, TransparencyAttrib
from direct.interval.LerpInterval import LerpHprInterval
from panda3d.core import loadPrcFile
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.fsm.FSM import FSM
from direct.interval.LerpInterval import LerpScaleInterval, LerpColorScaleInterval
from direct.interval.MetaInterval import Sequence

from lib import menuBars

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

    # Menu node
    self.node = NodePath("MenuNode")
    self.node.reparentTo(render)

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
  

  def enterTitle(self):

    """
    Enter title screen menu.
    """

    self.titleNode.show()
    self.accept("f1", self.request, ['Main'])

  def exitTitle(self):

    """
    Exit title screen menu.
    """

    logoLerp = Sequence(
      LerpScaleInterval(self.logo, 1.75, 5, 1),
      LerpColorScaleInterval(self.logo, .5, (1,1,1,0), (1,1,1,1))
    )
    logoLerp.start()

    taskMgr.doMethodLater(2.25, self.titleNode.hide, "MenuHideTitle", extraArgs=[])


    self.ignore("f1")

  def enterMain(self):

    """
    Enter main menu.
    """

    self.mainNode = NodePath("MenuMain")
    self.mainNode.reparentTo(aspect2d)

    OPTIONS = {
      'Online'  :   'Online',
      'Local'   :   'Local',
      'Options' :   'Options',
      'Quit'    :   'Quit'
    }

  def exitMain(self):

    """
    Exit main menu.
    """

    self.mainNode.hide()


  def windowEvent(self, window = None):

    """
    Update window size info everytime a window event occurs.
    """

    self.winWidth = base.win.getProperties().getXSize() 
    self.winHeight = base.win.getProperties().getYSize()
    self.winAspect = float(self.winWidth) / float(self.winHeight)    

m = mainMenu()
m.request("Title")
run()
