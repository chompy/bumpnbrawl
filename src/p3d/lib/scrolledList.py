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

    # Add items
    for i in range(len(items)):
      itemText = OnscreenText(text = items[i], pos = (.076, -.14 + (i* -.1)), scale = 0.07, align=TextNode.ALeft, fg=(1,1,1,1), parent=self.itemsNode, font=self.regFont)
      if i > 13: itemText.hide()
      self.items.append(itemText)

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

  def acceptInput(self):

    """
    Setup input to control scrolled list.
    """

    self.accept("wheel_up", self.scrollList, [-1])
    self.accept("wheel_down", self.scrollList, [1])  
    
