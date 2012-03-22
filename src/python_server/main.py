import asyncore
import socket

# MESSAGE ID REFERENCE
USERNAME = chr(1)
USERID = chr(2)
JOIN_CHANNEL = chr(3)
CLIENT_DATA = chr(4)    # NO OF CHARACTERS:
CHARACTER_DATA = chr(5) # CHAR SLOT:CHAR COLOR CODE:CHAR SKIN:CHAR NAME/playername [012chompy/Renoki]
PLAYER_INPUT = chr(6)
POSITION = chr(7)
#CHAT = chr(4)

class BnBClientHandler(asyncore.dispatcher_with_send):

  def __init__(self, sock, userid):

    asyncore.dispatcher_with_send.__init__(self, sock)
    self.buffer = ""
    self.prepareMsg(USERNAME, "")

    # Vars
    self.name = None
    self.id = userid
    self.isActive = True
    self.channel = None
    self.playerData = {}
    self.players = {}

  def handle_read(self):
    data = self.recv(1024)
    if not data: return None

    split = data.split("\n")

    for data in split:

      if not data: continue

      msgId = data[0]
      data = data[1:]

      # Retrieve Player Username
      if msgId == USERNAME:
        self.name = data
        print "Player #%s username is %s." % (str(self.id), self.name)

        self.prepareMsg(USERID, chr(self.id))     

      # Retrieve Channel Join Request
      elif msgId == JOIN_CHANNEL:
        channelId = ord(data[0])

        joinChannel = server.joinChannel(channelId, self)

        if joinChannel:
          print "Player #%s has joined channel #%s." % (str(self.id), channelId)
          self.channel = channelId
          
        else:
          print "Player #%s requested to join channel #%s but the channel is full." % (str(self.id), channelId)      
 
        self.prepareMsg(JOIN_CHANNEL, chr( int(joinChannel) ))

      # Retrieve Character Data
      elif msgId == CHARACTER_DATA:

        slot = int(ord(data[0]))
        color = int(ord(data[1]))
        skin = int(ord(data[2]))
        name = str(data[3:])

        if name:
          self.playerData[slot] = [name, color, skin]
          print "Player #%s sent character data for local slot #%s." % (str(self.id), str(slot))

          # Send my character data to everyone
          for i in server.users:
            if not i == self:
              i.prepareMsg(CHARACTER_DATA, chr(self.id) + chr(slot) + chr(color) + chr(skin) + name)

          # Get everyone's player data
          for i in server.users:
            if not i == self:
              for x in i.playerData:
                self.prepareMsg(CHARACTER_DATA, chr(i.id) + chr(x) + chr(i.playerData[x][1]) + chr(i.playerData[x][2]) + i.playerData[x][0])
          
        else:
          del self.playerData[slot]
        

      # Player Input
      elif msgId == PLAYER_INPUT:

        pInput = str(data)

        print "Player #%s sent input '%s'." % (str(self.id), pInput)

        # Send to other players
        for i in server.users:
          if i.channel == self.channel and not i == self and self.channel > 0:
            i.prepareMsg(PLAYER_INPUT, chr(self.id) + pInput)

      # Player Position/Dir
      elif msgId == POSITION:

        slot = int(ord(data[0]))

        otherData = data[1:].split("x")
        x = float(otherData[0])
        y = float(otherData[1])
        z = float(otherData[2])
        h = float(otherData[3])

        for i in server.users:
          if not i == self:
            i.prepareMsg(POSITION, chr(self.id) + chr(slot) + str(x) + "x" + str(y) + "x" + str(z) + "x" + str(h))

      else:
        print "Player #%s sent unrecognized message type, #%s." % (str(self.id), str(ord(msgId)))
             

  def prepareMsg(self, msgType, msg):

    """
    Prepare a message to be sent.
    """

    self.buffer = msgType + msg + "\n"

  def writable(self):
    return (len(self.buffer) > 0)

  def handle_write(self):
    sent = self.send(self.buffer)
    if sent:
      self.buffer = self.buffer[sent:]
    else:
      self.buffer = ""

  def handle_close(self):
    print "Player #%s has disconnected." % str(self.id)

    server.clearUserFromChannel(self.channel, self.id)
    self.close()
    self.isActive = False
    self.channel = None    

class BnBServer(asyncore.dispatcher):

  def __init__(self, host, port):

    # Vars
    self.users = []
    self.idCt = 0

    # Network Init
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.set_reuse_addr()
    self.bind((host, port))
    self.listen(5)

    self.channels = {}
    self.channelMode = {}   # Channel Modes: 0 = Lobby; 1 = Game Play

    print "BumpNBrawl Server v1 - Server started on port %s." % str(port)

  def test(self):
    return "YEP WORKING"

  def handle_accept(self):
    pair = self.accept()
    if pair is None:
      pass
    else:
      sock, addr = pair

      myId = None
      for i in range(self.idCt):
        if not self.users[i].isActive:
          myId = i
          self.users[i].__init__(sock, myId)
          break
          
      if not myId:
        self.idCt += 1  
        myId = self.idCt

        handler = BnBClientHandler(sock, myId)
        self.users.append(handler)

      print 'New Player connected with ID # %s from %s.' % (str(myId), repr(addr))

  def joinChannel(self, chanId, client):

    if chanId > 255: return False
    if chanId < 0: return False

    try:
      self.channels[chanId]
    except:
      self.channels[chanId] = []
      self.channelMode[chanId] = 1

    if len(self.channels[chanId]) >= 8:
      return False

    self.channels[chanId].append(client)
    return True

  def clearUserFromChannel(self, chanId, userId):

    if chanId > 255: return False
    if chanId < 0: return False    
    for y in range(len(self.channels[chanId])):
      if self.channels[chanId][y].id ==  userId:
        self.channels[chanId].remove(self.channels[chanId][y])
        print "Player #%s has left channel #%s." % (str(userId), str(chanId))
        break
      
          
    

server = BnBServer('localhost', 31592)
asyncore.loop()

