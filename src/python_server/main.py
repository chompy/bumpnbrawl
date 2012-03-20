from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import asyncore
import socket

# MESSAGE ID REFERENCE
USERNAME = chr(1)
USERID = chr(2)
POSITION = chr(3)
CHAT = chr(4)

class BnBClientHandler(asyncore.dispatcher_with_send):

  def __init__(self, sock, userid):

    asyncore.dispatcher_with_send.__init__(self, sock)
    self.buffer = ""
    self.prepareMsg(USERNAME, "")

    # Vars
    self.name = None
    self.id = userid
    self.isActive = True

  def handle_read(self):
    data = self.recv(1024)
    if not data: return None

    msgId = data[0]
    data = data[1:].strip()

    if msgId == USERNAME:
      self.name = data
      print "Player #%s username is %s." % (str(self.id), self.name)

      self.prepareMsg(USERID, chr(self.id))     

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
    self.close()
    self.isActive = False
      

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

        handler = BnBClientHandler(sock, myId)
        self.users.append(handler)

      print 'New Player connected with ID # %s from %s.' % (str(myId), repr(addr))        

server = BnBServer('localhost', 31592)
asyncore.loop()

