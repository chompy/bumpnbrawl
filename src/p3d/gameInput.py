from direct.showbase.DirectObject import DirectObject
from panda3d.core import loadPrcFile
from panda3d.core import ConfigVariableString
from lib import basePolling

try:
  hasPygame = True
  import pygame
except:
  hasPygame = False

class gameInput(DirectObject):

  def __init__(self):

    base.controls = {}
    self.loadControls()

    # Key Polling
    self.polling = basePolling.Interface()

    # Gamepad/Joystick Polling
    if hasPygame:
      print "PYGAME INIT"
      pygame.init()
      count = pygame.joystick.get_count() 
      self.__joysticks = [] 
      for i in range(count): 
        js = pygame.joystick.Joystick(i) 
        js.init() 
        self.__joysticks.append(js) 

      self.joyAxisDown = {}

      taskMgr.add(self.__on_joystick_polling, 'Joystick Polling') 

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

        # Network listeners
        self.accept(base.controls[y][i], messenger.send, ["network-send", ["player_input", i]])
        self.accept(base.controls[y][i] + "-up", messenger.send, ["network-send", ["player_input", i+"-up"]])

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


  def get_joysticks(self): 
    return self.__joysticks 
      
  def get_count(self): 
    return len(self.__joysticks) 
      
  def __on_joystick_polling(self, task): 

    """
    Task that polls the joysticks, sends events
    through Panda event handling system.
    """
    for ev in pygame.event.get(): 
      
      if ev.type is pygame.JOYBUTTONDOWN: 
        name = 'joy%d_btn%d' % (ev.joy + 1, ev.button + 1) 
        messenger.send(name)
        messenger.send("keyPoll", [name])
              
      elif ev.type is pygame.JOYBUTTONUP: 
        name = 'joy%d_btn%d-up' % (ev.joy + 1, ev.button + 1) 
        messenger.send(name)
        messenger.send("keyPoll", [name])
              
      elif ev.type is pygame.JOYAXISMOTION: 
        name = 'joy%d_axis%d' % (ev.joy + 1, ev.axis) 

        try: self.joyAxisDown[ev.joy]
        except KeyError: self.joyAxisDown[ev.joy] = {}

        try: self.joyAxisDown[ev.joy][ev.axis]
        except KeyError: self.joyAxisDown[ev.joy][ev.axis] = {'+':False, '-': False}

        if ev.value > 0:

          if ev.value < .5:
            if self.joyAxisDown[ev.joy][ev.axis]['-']:
              messenger.send(name + "--up") 
            self.joyAxisDown[ev.joy][ev.axis]['-'] = False

          else:
            if not self.joyAxisDown[ev.joy][ev.axis]['-']:
              messenger.send(name + "-")          
            self.joyAxisDown[ev.joy][ev.axis]['-'] = True            

          if abs(ev.value) > .5:            
            messenger.send("keyPoll", [name + "-"])
            
        elif ev.value < 0:
          if ev.value > -.5:
            if self.joyAxisDown[ev.joy][ev.axis]['+']:
              messenger.send(name + "+-up")
            self.joyAxisDown[ev.joy][ev.axis]['+'] = False
          else:
            if not self.joyAxisDown[ev.joy][ev.axis]['+']:
              messenger.send(name + "+")
            self.joyAxisDown[ev.joy][ev.axis]['+'] = True


          if abs(ev.value) > .5:
            messenger.send("keyPoll", [name + "+"])          
              
      #elif ev.type is pygame.JOYBALLMOTION: 
      #  name = 'joy%d_ball%d' % (ev.joy + 1, ev.hat) 
      #  events.append([name, ev.rel]) 
              
      elif ev.type is pygame.JOYHATMOTION: 
        name = 'joy%d_hat%d' % (ev.joy + 1, ev.hat) 
        direction = None
        if ev.value == (-1, 0):
          direction = "left"  
        elif ev.value == (0, 1):
          direction = "up"
        elif ev.value == (1, 0):
          direction = "right"
        elif ev.value == (0, -1):
          direction = "down"

        # Multi Directions
        elif ev.value == (-1,1):
          messenger.send(name + "_up")
          messenger.send("keyPoll", [name + "_up"])
          messenger.send(name + "_left")
          messenger.send("keyPoll", [name + "_left"])
          continue

        elif ev.value == (1,1):
          messenger.send(name + "_up")
          messenger.send("keyPoll", [name + "_up"])
          messenger.send(name + "_right")
          messenger.send("keyPoll", [name + "_right"])
          continue

        elif ev.value == (-1,-1):
          messenger.send(name + "_down")
          messenger.send("keyPoll", [name + "_down"])
          messenger.send(name + "_left")
          messenger.send("keyPoll", [name + "_left"])
          continue
        elif ev.value == (1,-1):
          messenger.send(name + "_down")
          messenger.send("keyPoll", [name + "_down"])
          messenger.send(name + "_right")
          messenger.send("keyPoll", [name + "_right"])
          continue       

        # Hat Btn Up
        if ev.value[0] == 0:
          messenger.send(name + "_left-up")
          messenger.send(name + "_right-up")
        if ev.value[1] == 0:
          messenger.send(name + "_up-up")
          messenger.send(name + "_down-up")

        if direction: 
          name += "_" + direction
          messenger.send(name)
          messenger.send("keyPoll", [name])
          
    return task.cont 


  
