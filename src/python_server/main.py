from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

# MESSAGE ID REFERENCE
USERNAME = chr(1)
USERID = chr(2)
POSITION = chr(3)
CHAT = chr(4)


class BnBServer(LineReceiver):

  def __init__(self, users, myid):
    self.users = users
    self.name = None
    self.id = myid

  def connectionMade(self):

    """
    Connect was made, send request for username.
    """

    print "New player connected with ID #" + str(self.id) + "."

    self.sendLine(USERNAME)

  def connectionLost(self, reason):

    """
    User disconnected, delete key.
    """

    print "Player #" + str(self.id) + " has disconnected."
  
    if self.users.has_key(self.name):
      del self.users[self.name]

  def lineReceived(self, line):

    """
    Message recieved from player client.
    """

    if not line: return None
  
    msgId = line[0]
    line = line[1:].strip()

    # Recieve and set Username. Send user ID in response
    if msgId == USERNAME:
      self.name = line
      self.sendMsg(USERID, chr(self.id))
      #self.sendLine("Welcome " + self.name)
      print "Recieved username "+ self.name + " from player #" + str(self.id) + "."

    # MsgID not recongized
    else:
      print "Player #" + str(self.id) + " sent message with ID #" + str(ord(msgId)) + ". No response available."
    

  def sendMsg(self, msgType, msg):

    """
    Handles sending a message of a certain type.
    """

    if not msgType or not msg: return None
    self.sendLine(msgType + msg)
      

  # THE FOLLOWING WERE PART OF THE EXAMPLE PROGRAM THAT THIS
  # SERVER IS BASED ON AND ARE JUST HERE FOR REFERENCE
  def handle_GETNAME(self, name):
    if self.users.has_key(name):
      self.sendLine("Name taken, please choose another.")
      return
    self.sendLine("Welcome, %s!" % (name,))
    self.name = name
    self.users[name] = self
    self.state = "CHAT"

  def handle_CHAT(self, message):
    message = "<%s> %s" % (self.name, message)
    for name, protocol in self.users.iteritems():
      if protocol != self:
        protocol.sendLine(message)


class BnBFactory(Factory):

  def __init__(self):
    self.users = {} # maps user names to Chat instances
    self.idCt = 0   # User ID Counter

    print "BumpNBrawl Server v1 - Server started."

  def buildProtocol(self, addr):
    self.idCt += 1  # Plus one to ID, set new user to this ID
    return BnBServer(self.users, self.idCt)

reactor.listenTCP(31592, BnBFactory())
reactor.run()


