from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode, NodePath, CardMaker,TextureStage, Texture, TransparencyAttrib
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Parallel
from direct.interval.LerpInterval import LerpPosInterval, LerpColorScaleInterval

class scrolledList(DirectObject):

  def __init__(self, items = None):

    """
    Setup a scrolled list.
    """

    # Load Fonts
    self.boldFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansBold.ttf")
    self.regFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansCondensed.ttf")    

    # Node
    self.node = NodePath("ScrolledList_Node")
    self.node.reparentTo(aspect2d)

    # Prepare menu BG
    menu_frame = CardMaker("ScrolledList_Background")
    menu_frame.setFrame(0,1.3,0,-1.5)
    menu_frame.setColor(0,0,0,.7)
    sLBG = self.node.attachNewNode(menu_frame.generate())
    sLBG.setTransparency(TransparencyAttrib.MAlpha)

    # Load Scroll Arrow Image
    self.scrollArrow = loader.loadTexture(base.assetPath + "/menu/scroll_arrow.png")

    # Scroll Buttons
    self.scrollUp = DirectButton( 
             scale=.04,
             frameColor=(.6,.6,.6,0), 
             pos=(1.245,0,-.06),
             image=self.scrollArrow,
             parent=self.node,            
             #frameTexture=self.arrowTex,
             relief=DGG.FLAT,
             rolloverSound=None,
             clickSound=None,
             command=self.scrollList,
             extraArgs=[-1]             
             ) 
    self.scrollUp.setTransparency(TransparencyAttrib.MAlpha)    
    self.scrollUp.hide()

    self.scrollDown = DirectButton( 
             scale=.04,
             frameColor=(.6,.6,.6,0), 
             pos=(1.245,0,-1.445),
             image=self.scrollArrow,
             parent=self.node,            
             #frameTexture=self.arrowTex,
             relief=DGG.FLAT,
             rolloverSound=None,
             clickSound=None,
             hpr=(180,0,180),
             command=self.scrollList,
             extraArgs=[1]
             ) 
    self.scrollDown.setTransparency(TransparencyAttrib.MAlpha)  

    # Items Node
    self.itemsNode = NodePath("ScrolledList_Items")
    self.itemsNode.reparentTo(self.node)
    self.items = []

    # Set Items
    self.setItems([
      'Test','Pewp','Porkchops','Cookies','Tubes',  'Test','Pewp','Porkchops','Cookies','Tubes',  'Test','Pewp','Porkchops','Cookies','Tubes',  'Test','Pewp','Porkchops','Cookies','Tubes'
    ])

    self.acceptInput()
    
  def setItems(self, items):

    """
    Setup item list.
    """

    # Remove previous list.
    del self.items
    self.itemsNode.removeNode()

    # Make new node.
    self.itemsNode = NodePath("ScrolledList_Items")
    self.itemsNode.reparentTo(self.node)
    self.items = []
    self.scroll = 0
    self.selected = 0

    # Add items
    for i in range(len(items)):

      itemBtn = DirectButton( 
               text=items[i], 
               text_fg=(1, 1, 1, 1), frameColor=(.6,.6,.6,0), 
               scale=.07, pos=(.076,0, -.12 + (i * -.1)), 
               parent=self.itemsNode,
               text_font=self.regFont,
               text_align=TextNode.ALeft,
               #frameTexture=self.arrowTex,
               frameSize=(-.25, 16.0, -.4, 1.0),
               relief=DGG.FLAT,
               rolloverSound=None,
               clickSound=None,
               command=self.selectItem,
               extraArgs=[i],            
               ) 

      #itemBtn.bind(DGG.WITHIN, self.itemHover, [itemBtn])
      #itemBtn.bind(DGG.WITHOUT, self.itemUnhover, [itemBtn])      
      if i > 13: itemBtn.hide()
      self.items.append(itemBtn)

    # Hide Scroll Down Button if less then 14 items
    if len(self.items) < 14: self.scrollDown.hide()

  def scrollList(self, amt):

    """
    Scroll the list by a certain ammount.
    """

    if self.scroll + amt < 0: return None
    if self.scroll + amt > len(self.items) - 14: return None
    self.scroll += amt

    self.itemsNode.setZ(self.scroll * .1)

    for i in range(len(self.items)):
      if i >= self.scroll and i < self.scroll + 14:
        self.items[i].show()
      else:
        self.items[i].hide()

    # Hide/Show Scroll Arrows
    if self.scroll >= len(self.items) - 14: self.scrollDown.hide()
    else: self.scrollDown.show()

    if self.scroll <= 0: self.scrollUp.hide()
    else: self.scrollUp.show()

  def selectItem(self, number):

    """
    Make item selection.
    """

    self.items[self.selected]['frameColor'] = (.6,.6,.6,0)

    self.selected = number
    self.items[self.selected]['frameColor'] = (.6,.6,.6,.4)

    # Adjust scroll if needed.
    if self.selected - self.scroll < 0:
      self.scrollList(self.selected - self.scroll)

    if self.selected - self.scroll > 13:
      self.scrollList(abs(13 - (self.selected - self.scroll)))

  def changeSelection(self, inc):

    """
    Change item selection with an increment.
    """

    newVal = self.selected + inc
    if newVal > len(self.items) - 1: newVal = 0
    if newVal < 0: newVal = len(self.items) - 1

    self.selectItem(newVal)

  def acceptInput(self):

    """
    Setup input to control scrolled list.
    """

    base.accept("wheel_up", self.scrollList, [-1])
    base.accept("wheel_down", self.scrollList, [1])  

    for x in range(4):
      base.accept("p" + str(x + 1) + "_up", self.changeSelection, [-1])
      base.accept("p" + str(x + 1) + "_down", self.changeSelection, [1]) 
