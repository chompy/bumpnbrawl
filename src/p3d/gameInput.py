from direct.showbase.DirectObject import DirectObject
from panda3d.core import loadPrcFile
from panda3d.core import ConfigVariableString

class gameInput(DirectObject):

  def __init__(self):

    self.controls = {}
    self.loadControls()

  def loadControls(self):

    del self.controls
    self.controls = {}

    # Set controls for all players.
    for x in range(0,4):
      y=str(3 - x+1)

      self.controls[y] = {
        'p'+y+'_up'   :   ConfigVariableString('p'+y+'-up', 'arrow_up').getValue(),
        'p'+y+'_down' :   ConfigVariableString('p'+y+'-down', 'arrow_down').getValue(),
        'p'+y+'_left' :   ConfigVariableString('p'+y+'-left', 'arrow_left').getValue(),
        'p'+y+'_right':   ConfigVariableString('p'+y+'-right', 'arrow_right').getValue(),
        'p'+y+'_btna' :   ConfigVariableString('p'+y+'-btna', 'shift').getValue(),
        'p'+y+'_btnb' :   ConfigVariableString('p'+y+'-btnb', 'z').getValue()
      }

      # Bind keys to specific game event
      for i in self.controls[y]:
        base.accept(self.controls[y][i], messenger.send, [i])
        base.accept(self.controls[y][i] + "-up", messenger.send, [i+"-up"])
        
