from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode, NodePath
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import LerpColorScaleInterval

KBD_REPLACE = {
  'arrow_up'    :   'up',
  'arrow_down'  :   'down',
  'arrow_left'  :   'left',
  'arrow_right' :   'right'
}

class inputHelp():

  """
  Displays information on what
  keyboard/gamepad buttons do.

  REQUIRES: base.controls to be set.
  """

  def __init__(self, options):

    # Fonts
    self.boldFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansBold.ttf")    
    self.regFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansCondensed.ttf")

    # NodePath
    self.node = NodePath("InputHelp")
    self.node.reparentTo(aspect2d)

    # Vars
    self.optionList = []

    # Set Options
    self.setOptions(options)

  def setOptions(self, options):

    """
    Shows input options.
    """

    # Fade Out

    # Destroy old options
    for i in self.optionList:

      lerp = LerpColorScaleInterval(i[0], .5, (1,1,1,0))
      lerp.start()

      lerp = LerpColorScaleInterval(i[1], .5, (1,1,1,0))
      lerp.start()
    
      taskMgr.doMethodLater(1, i[0].destroy, "InputHelp_DestroyHelpItem", extraArgs=[])
      taskMgr.doMethodLater(1, i[1].destroy, "InputHelp_DestroyHelpKey", extraArgs=[])

    del self.optionList
    self.optionList = []

    if len(options) <= 0: return None

    # Fade In


    xoffset = 0

    # Go through all options, display them.
    for i in range(len(options)):

      # Display name of input event
      helpItem = OnscreenText(
        text = options[i][0] + ":",
        fg=(1,1,1,1), 
        shadow=(0,0,0,.6),
        align=TextNode.ALeft, 
        font=self.regFont, 
        pos = (xoffset, 0), 
        scale = 0.05, 
        parent=self.node
        )  

      # Set X offset
      pos1,pos2 = helpItem.getTightBounds()
      xoffset += (pos2[0] - pos1[0]) + .02

      # Gey key name
      key = self.getEventKey(options[i][1])

      # Display input trigger key
      keyItem = OnscreenText(
        text = key,
        fg=(1,1,1,1), 
        shadow=(0,0,0,.6),
        align=TextNode.ALeft, 
        font=self.boldFont, 
        pos = (xoffset, 0), 
        scale = 0.04, 
        parent=self.node
        )     

      # Set X offset
      pos1,pos2 = keyItem.getTightBounds()
      xoffset += (pos2[0] - pos1[0]) + .05 

      # Fade In
      lerp = LerpColorScaleInterval(helpItem, .5, (1,1,1,1), (1,1,1,0))
      lerp.start()

      lerp = LerpColorScaleInterval(keyItem, .5, (1,1,1,1), (1,1,1,0))
      lerp.start()

      # Add text to array to destroy later.
      self.optionList.append([helpItem, keyItem])

  def getEventKey(self, event):

    """
    Returns the key to display for a given event.
    """

    # Get input trigger key
    key = None
    for x in base.controls:
      for y in base.controls[x]:
        if y == event:
          key = base.controls[x][y]
          break          

    try:
      key = KBD_REPLACE[key]
    except KeyError: 1

    if not key: return event
    return key.strip()
            

      
