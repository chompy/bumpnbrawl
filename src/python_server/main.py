import asyncore
import socket

# MESSAGE ID REFERENCE
USERNAME = chr(1)
USERID = chr(2)
JOIN_CHANNEL = chr(3)
CLIENT_DATA = chr(4)    # NO OF CHARACTERS:
CHARACTER_DATA = chr(5) # CHAR SLOT:CHAR COLOR CODE:CHAR SKIN:CHAR NAME/playername [012chompy/Renoki]
#POSITION = chr(3)
#CHAT = chr(4)

class BnBClientHandler(asyncore.dispatcher_with_send):

  def __init__(self, sock, userid, server):

    asyncore.dispatcher_with_send.__init__(self, sock)
    self.buffer = ""
    self.prepareMsg(USERNAME, "")

    # Vars
    self.server = server
    self.name = None
    self.id = userid
    self.isActive = True
    self.channel = None

  def handle_read(self):
    data = self.recv(1024)
    if not data: return None

    msgId = data[0]
    data = data[1:]

    if msgId == USERNAME:
      self.name = data
      print "Player #%s username is %s." % (str(self.id), self.name)

      self.prepareMsg(USERID, chr(self.id))     

    elif msgId == JOIN_CHANNEL:
      channelId = ord(data[0])

      joinChannel = self.server.joinChannel(channelId, self)

      if joinChannel:
        print "Player #%s request to join channel #%s. Channel Full." % (str(self.id), channelId)      
      else:
        print "Player #%s request to join channel #%s." % (str(self.id), channelId)
      
      self.prepareMsg(JOIN_CHANNEL, chr( int(joinChannel) ))

    else:
      print "Player #%s sent unrecognized message type, #%s." % str(ord(msgId))
             

  def prepareMsg(self, msgType, msg):

    """
    Prepare a message to be sent.
    """

    self.buffer = msgType + msg

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
    self.server.clearUserFromChannel(self.channel, self.id)
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

    print "BumpNBrawl Server v1 - Server started on port %s." % str(port)

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

        handler = BnBClientHandler(sock, myId, self)
        self.users.append(handler)

      print 'New Player connected with ID # %s from %s.' % (str(myId), repr(addr))

  def joinChannel(self, chanId, client):

    if chanId > 255: return False
    if chanId < 0: return False

    try:
      self.channels[chanId]
    except:
      self.channels[chanId] = []

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
        break
      
          
    

server = BnBServer('localhost', 31592)
asyncore.loop()

