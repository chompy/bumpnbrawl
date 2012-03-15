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

    # Vars
    self.selected = 0

  def setOptions(self, options):

    """
    Sets up a menu bar with options.
    """

    addTime = 0.0
    if len(self.buttons) >= 0:
      for i in range(len(self.buttons)):
        self.buttons[i].unbind(DGG.WITHIN)
        self.buttons[i].unbind(DGG.WITHOUT) 
        self.buttonMouseOut(self.buttons[i])
        lerp = LerpPosInterval(self.buttons[i], .5, (self.buttons[i].getX(), self.buttons[i].getY(), -2.5)) 
        taskMgr.doMethodLater(float((len(self.buttons) - i) + .01) * .25, lerp.start, "MenuBar_Buttons_OldScrollOut_" + str(i), extraArgs=[])
        taskMgr.doMethodLater(float(len(self.buttons) * 1.0), self.buttons[i].destroy, "MenuBar_Buttons_OldCleanup_" + str(i), extraArgs=[])
      addTime = float(len(self.buttons) * .3)
      del self.buttons
      self.buttons = []

    if len(options) <= 0: return None

    for i in range(len(options)):
      DB = DirectButton( 
               text=options[i][0], 
               text_fg=(1, 1, 1, 1), frameColor=(1,1,1,1), 
               text_wordwrap=10, 
               scale=.1, pos=(0,0,i * -.18), 
               command=options[i][1],
               extraArgs=options[i][2],
               parent=self.node,
               text_font=self.barFont,
               frameTexture=self.barTex,
               frameSize=(-4, 4, -.8, .8),
               relief=DGG.FLAT,
               text_pos=(.75,-.3),
               rolloverSound=None,
               clickSound=None               
               ) 
      DB.setTransparency(TransparencyAttrib.MAlpha)
      DB.setX(-.1)            

      taskMgr.doMethodLater(addTime + len(options) * .4, DB.bind, "MenuBar_Buttons_" + str(i) + "_BindMouseTask", extraArgs=[DGG.WITHIN, self.buttonMouseOn, [DB]])
      taskMgr.doMethodLater(addTime + len(options) * .4, DB.bind, "MenuBar_Buttons_" + str(i) + "_BindMouseTask", extraArgs=[DGG.WITHOUT, self.buttonMouseOut, [DB]])      

      self.buttons.append(DB)

      # Setup a lerp interval to stack in
      lerp = LerpPosInterval(DB, .5, DB.getPos()) 
      DB.setPos((DB.getX(), DB.getY(), DB.getZ() + 1.0))

      taskMgr.doMethodLater(addTime + float( (len(options) - i) + .01) * .25, lerp.start, "MenuBars_Button_" + str(i) + "_LerpStackIn", extraArgs=[])

    # Set Player 1 input
    self.deactivateKeyboard()

    self.selected = 0
    self.keyboardSelect(0)
      
  def buttonMouseOn(self, button, mouse = None):

    """
    Actviates when the mouse hovers a button.
    """
  
    for i in range(len(self.buttons)):
      if self.buttons[i] == button: 
        self.selected = i
      else:
        self.buttonMouseOut(self.buttons[i])
          
    lerp = LerpPosInterval(button, .25, (-0,button.getY(),button.getZ()))
    lerp.start()

  def buttonMouseOut(self, button, mouse = None):

    """
    Activates when the mouse stop hovering a button.
    """
  
    lerp = LerpPosInterval(button, .25, (-.1,button.getY(),button.getZ()))
    lerp.start()

  def activateKeyboard(self):

    """
    Activates keyboard input, allowing player 1 to make bar
    menu go up and down with arrow keys.
    """
  
    base.accept("p1_up", self.keyboardSelect, [-1])
    base.accept("p1_down", self.keyboardSelect, [1]) 

    self.keyboardSelect(0)   

  def deactivateKeyboard(self):

    """
    Deactivate keyboard.
    """

    base.accept("p1_up", self.activateKeyboard)
    base.accept("p1_down", self.activateKeyboard)
    base.ignore("p1_btna")


  def keyboardSelect(self, direction):

    """
    Selects the active button with the keyboard.
    Binds the button function to p1-btna.
    """
  
    for i in self.buttons:
      self.buttonMouseOut(i)

    self.selected += direction
    if self.selected > len(self.buttons) - 1: self.selected = 0
    elif self.selected < 0: self.selected = len(self.buttons) - 1

    base.accept("p1_btna", self.buttons[self.selected]['command'], self.buttons[self.selected]['extraArgs'])
    self.buttonMouseOn(self.buttons[self.selected])
