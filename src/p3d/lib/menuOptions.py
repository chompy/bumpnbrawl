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

    # Vars
    self.optionNodes = []
    self.scrollOptions = {}

  def setOptions(self, options):

    if len(self.optionNodes) > 0:
    
      for i in range(len(self.optionNodes)):

        lerp = LerpColorScaleInterval(self.optionNodes[i][0], .7, (1,1,1,0))
        lerp.start()
              
        taskMgr.doMethodLater(1, self.optionNodes[i][1].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_1", extraArgs=[])
        taskMgr.doMethodLater(1, self.optionNodes[i][2].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_2", extraArgs=[])
        taskMgr.doMethodLater(1, self.optionNodes[i][3].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_3", extraArgs=[])
        taskMgr.doMethodLater(1, self.optionNodes[i][4].destroy, "MenuOptions_DestroyOptionNode_" + str(i) + "_4", extraArgs=[])
        taskMgr.doMethodLater(1, self.optionNodes[i][0].removeNode, "MenuOptions_DestroyOptionNode_" + str(i) + "_0", extraArgs=[])
        

      del self.optionNodes
      self.optionNodes = []

    if len(options) <= 0: return None

    for i in range(len(options)):

      optionNode = NodePath("MenuOptions_OptionNode_" + str(i))
      optionNode.reparentTo(self.node)
      optionNode.setZ(-i * .275)

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
      optionSelector.setTransparency(TransparencyAttrib.MAlpha)

      # Setup scroll list
      self.scrollOptions[i] = []
      for x in range(len(options[i][1])):
        self.scrollOptions[i].append(options[i][1][x])

      optionSelector.setText(self.scrollOptions[i][0][0])

      # Change Option Left Button
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

