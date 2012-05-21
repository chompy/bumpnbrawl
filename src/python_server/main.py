import asyncore
import socket
from network_events import clientConfirm

# MESSAGE ID REFERENCE
CLIENT_CONFIRM = chr(1)
CLIENT_ID = chr(2)


class BnBClientHandler(asyncore.dispatcher_with_send):

  def __init__(self, sock, userid):

    asyncore.dispatcher_with_send.__init__(self, sock)
    self.buffer = ""

    # Vars
    self.id = userid
    self.isActive = True
    self.gameChannel = None
    self.clientConfirm = False
    
    self.playerData = {}

    self.prepareMsg(CLIENT_CONFIRM, "")

  def handle_read(self):

    """
    Handles reading incoming network data.
    """

    # Recieve 1024 bytes
    data = self.recv(1024)

    # Done if no data was sent.
    if not data: return None

    # Split data up by line.
    split = data.split("\n")

    # Read data line by line.
    for data in split:

      # If no data continue to next line.
      if not data: continue

      # Get Message ID (The first character)
      msgId = data[0]

      # Get the data sent.
      data = data[1:]    

      # Determine what type of message was sent.

      # Client Confirm (Security Check)
      if msgId == CLIENT_CONFIRM:
        clientConfirm.clientConfirm(self, data)

      elif not self.clientConfirm:
        self.close()
        

  def prepareMsg(self, msgType, msg):

    """
    Prepare a message to be sent.
    """

    # Add message to buffer (will get sent later).
    self.buffer += msgType + msg + "\n"

  def writable(self):

    """
    Not sure?
    """
  
    return (len(self.buffer) > 0)

  def handle_write(self):

    """
    Handles sending data to clients.
    """
  
    sent = self.send(self.buffer)
    if sent:
      self.buffer = self.buffer[sent:]
    else:
      self.buffer = ""

  def handle_close(self):

    """
    Handles client disconnect event.
    """
  
    print "Player #%s has disconnected." % str(self.id)

    # Send disconnect to other clients
    for x in server.users:
      if not x == self:
        for y in self.playerData:
          x.prepareMsg(CHARACTER_DATA, chr(self.id) + chr(y) + chr(0) + chr(0) + chr(0) )

    # Close connection
    server.clearUserFromChannel(self.channel, self.id)
    self.close()
    self.isActive = False
    self.channel = None              

class BnBServer(asyncore.dispatcher):

  def __init__(self, host, port):

    # Vars
    self.clients = []
    self.idCt = 0
    self.gameChannels = {}

    # Network Init
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.set_reuse_addr()
    self.bind((host, port))
    self.listen(5)

    # Print a message saying server has started.
    print "BumpNBrawl Server v2 - Server started on port %s." % str(port)

  def handle_accept(self):

    """
    Handles new client connections.
    """
  
    pair = self.accept()
    if pair is None:
      pass
    else:
      sock, addr = pair

      # Find an ID to grant new client.
      myId = None
      for i in range(self.idCt):
        if not self.clients[i].isActive:
          myId = i
          self.clients[i].__init__(sock, myId)
          break
          
      if not myId:
        self.idCt += 1  
        myId = self.idCt

        handler = BnBClientHandler(sock, myId)
        self.clients.append(handler)

      print 'New client connected with ID # %s from %s.' % (str(myId), repr(addr))
          
    

server = BnBServer('', 31592)
asyncore.loop()

