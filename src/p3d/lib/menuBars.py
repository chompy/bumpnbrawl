from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode, NodePath, CardMaker,TextureStage, Texture, TransparencyAttrib
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpPosInterval

class menuBars(DirectObject):

  """
  Makes a list of selectable items.
  """

  def __init__(self, options):

    # Set Node
    self.node = NodePath("MenuBarNode")
    self.node.reparentTo(aspect2d)

    # Load Fonts
    self.barFont = loader.loadFont(base.assetPath + "/fonts/badaboombb.ttf")    
    self.barFont.setPixelsPerUnit(60)

    # Load Menubar Texture
    self.barTex = loader.loadTexture(base.assetPath + "/menu/menubar.png")

    # Button List
    self.buttons = []


  def setOptions(self, options):

    if len(self.buttons) > 0:
      for i in self.buttons:
        i.destroy()
      del self.buttons
      self.buttons = []

    if len(options) <= 0: return None

    for i in range(len(options)):
      DB = DirectButton( 
               text=options[i][0], 
               text_fg=(1, 1, 1, 1), frameColor=(1,1,1,1), 
               text_wordwrap=10, 
               scale=.1, pos=(0,0,i * -.18), 
               #command=, 
               parent=self.node,
               text_font=self.barFont,
               frameTexture=self.barTex,
               frameSize=(-4, 4, -.8, .8),
               relief=DGG.FLAT,
               text_pos=(.5,-.3),
               rolloverSound=None,
               clickSound=None               
               ) 
      DB.setTransparency(TransparencyAttrib.MAlpha)
      DB.setX(-.1)            

      DB.bind(DGG.WITHIN, self.buttonMouseOn, [DB])
      DB.bind(DGG.WITHOUT, self.buttonMouseOut, [DB])

      self.buttons.append(DB)

      # Setup a lerp interval to stack in
      lerp = LerpPosInterval(DB, .5, DB.getPos()) 
      DB.setPos((DB.getX(), DB.getY(), DB.getZ() + 1.0))

      taskMgr.doMethodLater(float( (len(options) - i) + .01) * .25, lerp.start, "MenuBars_Button_" + str(i) + "_LerpStackIn", extraArgs=[])
      
  def buttonMouseOn(self, button, mouse):
    lerp = LerpPosInterval(button, .25, (-0,button.getY(),button.getZ()), (-.1,button.getY(),button.getZ()))
    lerp.start()

  def buttonMouseOut(self, button, mouse):
    lerp = LerpPosInterval(button, .25, (-.1,button.getY(),button.getZ()), (0,button.getY(),button.getZ()))
    lerp.start()
