from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode, NodePath, CardMaker,TextureStage, Texture, TransparencyAttrib
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import Parallel
from direct.interval.LerpInterval import LerpPosInterval, LerpColorScaleInterval

class menuOptions(DirectObject):

  def __init__(self, options):

    # Set Node
    self.node = NodePath("MenuOptionsNode")
    self.node.reparentTo(aspect2d)

    # Load Fonts
    self.boldFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansBold.ttf")
    self.regFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansCondensed.ttf")

    # Load Select Arrow Texture
    self.arrowEnabled = loader.loadTexture(base.assetPath + "/menu/select_arrow_enabled.png")
    self.arrowDisabled = loader.loadTexture(base.assetPath + "/menu/select_arrow_disabled.png")    
    self.arrowKbdSelect = loader.loadTexture(base.assetPath + "/menu/keyboard_select.png")        

    # Vars
    self.optionNodes = []
    self.scrollOptions = {}
    self.selected = 0

  def setOptions(self, options):

    base.ignore("p1_left")
    base.ignore("p1_right")

    if len(self.optionNodes) > 0:
    
      for i in range(len(self.optionNodes)):

        lerp = LerpColorScaleInterval(self.optionNodes[i][0], .7, (1,1,1,0))
        lerp.start()
              
        taskMgr.doMethodLater(1, self.optionNodes[i][1].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_1", extraArgs=[])
        taskMgr.doMethodLater(1, self.optionNodes[i][2].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_2", extraArgs=[])
        if self.optionNodes[i][3]:
          taskMgr.doMethodLater(1, self.optionNodes[i][3].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_3", extraArgs=[])
        if self.optionNodes[i][4]:
          taskMgr.doMethodLater(1, self.optionNodes[i][4].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_4", extraArgs=[])
        taskMgr.doMethodLater(1, self.optionNodes[i][0].removeNode, "MenuOptions_DestroyOptionNode_" + str(i) + "_0", extraArgs=[])
        

      del self.optionNodes
      self.optionNodes = []

    if len(options) <= 0: return None

    for i in range(len(options)):

      #optionNode = NodePath("MenuOptions_OptionNode_" + str(i))
      optionNode = DirectFrame(
        frameSize=(-.1, .9, -.15, .1),
        frameColor=(1,1,1,0),
        pos=(0,0,-i * .275),
        parent=self.node,
      )
      optionNode.setTransparency(TransparencyAttrib.MAlpha)
      
      # Option Name Text
      optionName = OnscreenText(
        text = options[i][0], 
        fg=(1,1,1,1), 
        shadow=(0,0,0,.6),
        align=TextNode.ALeft, 
        font=self.regFont, 
        pos = (0, 0), 
        scale = 0.07, 
        parent=optionNode
        )

      # Option Scroll List
      if len(options[i][1]) > 1:      
        optionSelector = OnscreenText(
          text = 'menu option', 
          fg=(1,1,1,1), 
          shadow=(0,0,0,.6),
          align=TextNode.ACenter, 
          font=self.boldFont, 
          pos = (.37, -.107), 
          scale = 0.05, 
          parent=optionNode,
          mayChange=True
          )
      else:
        optionSelector = DirectButton(
          text = 'menu option',
          rolloverSound=None,
          clickSound=None,
          frameColor=(0,0,0,0),
          text_fg = (1,1,1,1),
          text_shadow = (0,0,0,.6),
          text_align=TextNode.ACenter, 
          text_font=self.boldFont,           
          pos = (.37,0, -.107), 
          scale = 0.05,
          parent=optionNode,
          command=options[i][1][0][1],
          extraArgs=options[i][1][0][2],      
        )
      optionSelector.setTransparency(TransparencyAttrib.MAlpha)

      # Setup scroll list
      self.scrollOptions[i] = []
      for x in range(len(options[i][1])):
        self.scrollOptions[i].append(options[i][1][x])

      # Get Default
      try:
        default = options[i][2]
      except IndexError:
        default = 0

      if len(options[i][1]) > 1:
        optionSelector.setText(self.scrollOptions[i][default][0])
      else:
        optionSelector['text'] = self.scrollOptions[i][0][0]

      # Change Option Left Button
      btnLeft = None
      btnRight = None
      if len(options[i][1]) > 1:
        btnLeft = DirectButton( 
                 text="", 
                 text_fg=(1, 1, 1, 1), frameColor=(1,1,1,0), 
                 scale=.05, pos=(.09,0,-.09), 
                 hpr=(180,0,0),
                 command=self.scrollOption,
                 extraArgs=[-1, optionSelector, self.scrollOptions[i]],
                 parent=optionNode,
                 #frameTexture=self.arrowTex,
                 #frameSize=(-4, 4, -.8, .8),
                 image=self.arrowEnabled,
                 relief=DGG.FLAT,
                 rolloverSound=None,
                 clickSound=None               
                 ) 
        btnLeft.setTransparency(TransparencyAttrib.MAlpha)        

        # Change Option Right Button
        btnRight = DirectButton( 
                 text="", 
                 text_fg=(1, 1, 1, 1), frameColor=(1,1,1,0), 
                 scale=.05, pos=(.65,0,-.09), 
                 command=self.scrollOption,
                 extraArgs=[1, optionSelector, self.scrollOptions[i]],
                 parent=optionNode,
                 #frameTexture=self.arrowTex,
                 #frameSize=(-4, 4, -.8, .8),
                 image=self.arrowEnabled,
                 relief=DGG.FLAT,
                 rolloverSound=None,
                 clickSound=None               
                 ) 
        btnRight.setTransparency(TransparencyAttrib.MAlpha)            

      # Fade In
      lerp2 = LerpColorScaleInterval(optionNode, .7, (1,1,1,1), (1,1,1,0))
      lerp2.start()

      # Add Node to array
      self.optionNodes.append([
        optionNode,
        optionName,
        optionSelector,
        btnLeft,
        btnRight
      ])

    # Player 1 Input
    self.selected = default
    self.deactivateKeyboard()

  def scrollOption(self, direction, textNode, optionList):

    """
    Scrolls an option list to the next/last option.
    """      

    # Get the current option selected.
    for i in range(len(optionList)):
      if optionList[i][0] == textNode.getText():
        currentOption = i

        break

    # Increase/Decrease Option
    currentOption += direction

    # Make sure it's within the boundries of the optionList array.
    if currentOption < 0: currentOption = len(optionList) - 1
    elif currentOption > len(optionList) - 1: currentOption = 0

    # Execute Command [If specified]
    if optionList[currentOption][1]:
      optionList[currentOption][1](*optionList[currentOption][2])
    

    # Set Text

    seq1 = Parallel(
      LerpPosInterval(textNode, .25, (.2 * direction,-.107,0)),
      LerpColorScaleInterval(textNode, .25, (1,1,1,0), (1,1,1,1))
    )

    seq2 = Parallel(
      LerpPosInterval(textNode, .25, (0, -.107,0),(-.2 * direction,-.107,0)),
      LerpColorScaleInterval(textNode, .25, (1,1,1,1), (1,1,1,0))
    )
        
    seq1.start()

    taskMgr.doMethodLater(.25, textNode.setText, "MenuOptions_ScrollOptionTextChange", extraArgs=[optionList[currentOption][0]])
    taskMgr.doMethodLater(.25, seq2.start, "MenuOptions_ScrollOptionAnimation", extraArgs=[])

  def activateKeyboard(self):

    """
    Activate keyboard selection.
    """
  
    base.accept("p1_up", self.keyboardSelect, [-1])
    base.accept("p1_down", self.keyboardSelect, [1]) 

    self.keyboardSelect(0)

  def deactivateKeyboard(self):

    """
    Deactivate keyboard, ungray options.
    """

    base.accept("p1_up", self.activateKeyboard)
    base.accept("p1_down", self.activateKeyboard)
    base.ignore("p1_left")
    base.ignore("p1_right")
    base.ignore("p1_btna")

    for i in range(len(self.optionNodes)):
      node = self.optionNodes[i]
      color = (1,1,1,1)
      if node[3] and node[4]:
        node[3]['image'] = self.arrowEnabled
        node[4]['image'] = self.arrowEnabled       

      try:
        node[2].setFg(color)
      except:
        node[2]['text_fg'] = color

    self.accept("mouse1", self.deactivateKeyboard)

  def keyboardSelect(self, direction):

    """
    Sets the active option for keyboard selection.
    """

    self.selected += direction

    if self.selected > len(self.optionNodes) - 1:
      self.selected = 0
    elif self.selected < 0:
      self.selected = len(self.optionNodes) - 1
      
    for i in range(len(self.optionNodes)):
      node = self.optionNodes[i]

      if i == self.selected:    
        node[0]['image'] = self.arrowKbdSelect
        node[0]['image_scale']= .06
        node[0]['image_pos'] = (-.05,0,-.091)        
      else:
        node[0]['image'] = None


    # Set keyboard scroll
    base.ignore("p1_btna")
    base.ignore("p1_left")    
    base.ignore("p1_right")    
    if len(self.scrollOptions[self.selected]) > 1:
      base.accept("p1_right", self.scrollOption, [1, self.optionNodes[self.selected][2], self.scrollOptions[self.selected]])
      base.accept("p1_left", self.scrollOption, [-1, self.optionNodes[self.selected][2], self.scrollOptions[self.selected]])

    # Set button press
    else:
      if self.scrollOptions[self.selected][0][1]:
        base.accept("p1_btna", self.scrollOptions[self.selected][0][1], self.scrollOptions[self.selected][0][2])
    
        

      
      
