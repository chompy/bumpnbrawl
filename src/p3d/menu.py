# Import Panda3D Modules
from pandac.PandaModules import loadPrcFileData, TextNode, NodePath, CardMaker,TextureStage, Texture, VBase3
from direct.interval.LerpInterval import LerpHprInterval
from panda3d.core import loadPrcFile
from direct.gui.OnscreenText import OnscreenText

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

class mainMenu(ShowBase):

  def __init__(self):

    # Disable Mouse
    #base.disableMouse()

    # Menu node
    self.node = NodePath("MenuNode")
    self.node.reparentTo(render)

    # Prepare menu BG
    menu_frame = CardMaker("Menu_Background")
    menu_frame.setFrame(-1,1,-1,1)
    menu_frame.setColor(0.3843137254901961, 0.8509803921568627, 0.6117647058823529,1)
    menu_frame_node = self.node.attachNewNode(menu_frame.generate())
    menu_frame_node.setY(2)

    bgTex = loader.loadTexture(base.assetPath + "/menu/bg_overlay.png")

    #menu_frame_node.setTexture(bgTex)

    ts = TextureStage('PlayerHud_Snapshot_TextureStage')
    ts.setMode(TextureStage.MDecal)
    menu_frame_node.setTexture(ts, bgTex)    

    lerper = NodePath("Menu_Background_Lerper")
    menu_frame_node.setTexProjector(ts, NodePath(), lerper)
    menu_lerp = lerper.posInterval(60, VBase3(-1, 1, 0))
    menu_lerp.loop()

    run()

  def windowEvent(self, window = None):

    """
    Update window size info everytime a window event occurs.
    """

    self.winWidth = base.win.getProperties().getXSize() 
    self.winHeight = base.win.getProperties().getYSize()
    self.winAspect = float(self.winWidth) / float(self.winHeight)    

mainMenu()
