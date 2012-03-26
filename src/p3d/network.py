import asyncore,socket,struct,player
from direct.task.TaskManagerGlobal import taskMgr 
from direct.task import Task 

import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase

timeout_in_miliseconds=3000

# MESSAGE ID REFERENCE
USERNAME = chr(1)
USERID = chr(2)
JOIN_CHANNEL = chr(3)
CLIENT_DATA = chr(4)    # NO OF CHARACTERS:
CHARACTER_DATA = chr(5) # CHAR SLOT:CHAR COLOR CODE:CHAR SKIN:START SLOT:CHAR NAME/playername [012chompy/Renoki]
PLAYER_INPUT = chr(6)
POSITION = chr(7)
#CHAT = chr(4)

class networkHandler(asyncore.dispatcher):

  def __init__(self, host, port):

    asyncore.dispatcher.__init__(self)

    self.create_socket(socket.AF_INET,socket.SOCK_STREAM) 
    self.connect((host,port))
    self.buffer = ""

    self.name = "Chompy"
    self.id = None
    self.gameChannel = 1

    self.netPlayers = {}

    # Network send events
    base.accept("network-send", self.sendEventMsg)

  def handle_connect(self):
    print "Connected to host."

  def handle_close(self):
    self.close()

  def handle_read(self):

    data = self.recv(1024)
    if data <= 0: return None

    split = data.split("\n")

    for data in split:

      if not data: continue

      msgId = data[0]
      data = data[1:]

      # Send Player Username
      if msgId == USERNAME:
        print "Server is requesting username for %s." % self.name
        self.prepareMsg(USERNAME, self.name)

      # Retrieve User ID
      elif msgId == USERID:
        self.id = int(ord(data))
        print "Recieved ID#%s for player %s." % (str(self.id), self.name)

        # Join Channelo
        print "Attempting to join channel #%s." % str(self.gameChannel)
        self.prepareMsg(JOIN_CHANNEL, chr(self.gameChannel))
  
      # Join Channel Success
      elif msgId == JOIN_CHANNEL:
        success = bool(ord(data))

        if success:
          print "Joined channel #%s." % str(self.gameChannel)

          # Send Character data
          for i in base.players:
            if i.local:
              self.prepareMsg(CHARACTER_DATA, str(chr(int(i.controls)) + chr(int(1)) + chr(int(1)) + i.character))
          
        else:
          print "Failed to join channel #%s." % str(self.gameChannel)

      # Character data
      elif msgId == CHARACTER_DATA:

        pId = int(ord(data[0]))
        slot = int(ord(data[1]))
        color = int(ord(data[2]))
        skin = int(ord(data[3]))
        start = int(ord(data[4]))
        name = str(data[5:])

        if name:

          # If local player then we probably need start pos
          if pId == self.id:
            for i in base.players:
              if i.local and int(i.controls) == int(slot):            
                i.startPos = base.playerStart[start - 1]
                i.ode_body.setPosition(i.startPos[0], i.startPos[1], i.startPos[2] + 20.0 )     
                break
            return True             

          # If player already exists don't do anything
          try:
            for i in self.netPlayers[pId]:
              if i.controls == slot:
                return None
          except KeyError: 1
        
          char = player.player(name, False, slot, pId)
          base.players.append(char)

          try:
            self.netPlayers[pId].append(char)
          except:
            self.netPlayers[pId] = [char]        

        # If no character name given it's assumed we are removing this player slot.
        else:
          for i in base.players:
            if i.onlineId == pId and int(i.controls) == slot:
              # TODO: Player removal stuff. [Probably call function]
              print "Player removed. PID%s SLOT%s." % (str(pId), str(slot))
              self.netPlayers[pId].remove(i)
              i.destroy()

      # Get Player Inputs
      elif msgId == PLAYER_INPUT:

        pId = int(ord(data[0]))
        messenger.send(str(pId) + data[1:])
                      
      # Sync up player positions
      elif msgId == POSITION:   
        pId = int(ord(data[0]))
        slot = int(ord(data[1]))
        otherData = str(data[2:]).split("x")

        x = float(otherData[0])
        y = float(otherData[1])
        z = float(otherData[2])
        h = float(otherData[3])

        try:
          for i in self.netPlayers[pId]:
            if int(i.controls) == slot:
              i.ode_body.setPosition((x,y,z))
              i.actor.setH(h)
        except KeyError: 1

      else:

        print "Server sent unrecognized message id #%s." % str(ord(msgId))
        
    


  def prepareMsg(self, msgType, msg):

    """
    Prepares a message to be sent.
    """

    self.buffer += msgType + msg + "\n"

  def getMsgType(self, msgTypeStr):

    """
    Get message type from strings.
    """

    msgType = None
    if msgTypeStr == "character_data":
      msgType = CHARACTER_DATA
      
    elif msgTypeStr == "position":
      return POSITION
    elif msgTypeStr == "player_input":
      return PLAYER_INPUT
    else:
      return None

    return msgType

  def sendEventMsg(self, msgType, msg):
    self.prepareMsg(self.getMsgType(msgType), msg)
    
  def writable(self):
    return (len(self.buffer) > 0)

  def handle_write(self):
    sent = self.send(self.buffer)
    self.buffer = self.buffer[sent:]


  def __del__(self):
    self.handle_close()    

def doNetworkUpdate(task):
  asyncore.loop(count = 1, timeout=0)
  return task.cont

client = networkHandler("chompy.co", 31592)    
taskMgr.add(doNetworkUpdate, "NetworkLoop")

  
