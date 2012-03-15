from direct.showbase.DirectObject import DirectObject
from panda3d.core import loadPrcFile
from panda3d.core import ConfigVariableString
from lib import basePolling

class gameInput(DirectObject):

  def __init__(self):

    base.controls = {}
    self.loadControls()

    # Key Polling
    self.polling = basePolling.Interface()


  def loadControls(self):

    del base.controls
    base.controls = {}

    # Set controls for all players.
    for x in range(0,4):
      y=str(3 - x+1)

      base.controls[y] = {
        'p'+y+'_up'   :   ConfigVariableString('p'+y+'_up', 'arrow_up').getValue(),
        'p'+y+'_down' :   ConfigVariableString('p'+y+'_down', 'arrow_down').getValue(),
        'p'+y+'_left' :   ConfigVariableString('p'+y+'_left', 'arrow_left').getValue(),
        'p'+y+'_right':   ConfigVariableString('p'+y+'_right', 'arrow_right').getValue(),
        'p'+y+'_btna' :   ConfigVariableString('p'+y+'_btna', 'shift').getValue(),
        'p'+y+'_btnb' :   ConfigVariableString('p'+y+'_btnb', 'z').getValue()
      }

      # Bind keys to specific game event
      for i in base.controls[y]:
        base.accept(base.controls[y][i], messenger.send, [i])
        base.accept(base.controls[y][i] + "-up", messenger.send, [i+"-up"])

  def pollKeys(self, task = None):
    if not task:
      taskMgr.add(self.pollKeys, "GameInput_KeyPolling")
    else:
      l = self.polling.buttonsPressed()
      if len(l) > 0:
        for i in l:
          messenger.send("keyPoll", [i])
        
      return task.cont

  def stopPollKeys(self):
    taskMgr.remove("GameInput_KeyPolling")

  def setKey(self, event, key):

    # Open Conf File
    confFile = "../../assets/Config.prc"
    f = open(confFile, "r")
    confContents = f.readlines()
    f.close()

    # Look for entry
    append = True
    lines = []
    for i in confContents:
      if i.strip():
        line = i.strip().split(" ")
        if line[0] == event:
          line[1] = key
          append = False
        lines.append([line[0], line[1]])

    if append: lines.append([event, key])

    # Write
    confStr = ""
    for i in lines:
      confStr += i[0] + " " + i[1] + "\n"

    f = open(confFile, "w")
    f.write(confStr)
    f.close()
      
    del lines

    # Reload Keys
    loadPrcFile(confFile)
    self.loadControls()         



    
