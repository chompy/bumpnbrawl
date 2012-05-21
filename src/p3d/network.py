import asyncore,socket,struct,player
from direct.task.TaskManagerGlobal import taskMgr 
from direct.task import Task 

import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase
import time, math, hashlib

timeout_in_miliseconds=3000

CLIENT_VERSION = 1

# MESSAGE ID REFERENCE
CLIENT_CONFIRM = chr(1)
CLIENT_ID = chr(2)


class networkHandler(asyncore.dispatcher):

  def __init__(self, host, port):

    asyncore.dispatcher.__init__(self)

    self.create_socket(socket.AF_INET,socket.SOCK_STREAM) 
    self.connect((host,port))
    self.buffer = ""

    self.id = None
    self.gameChannel = None
    self.netPlayers = {}

    # Network send events
    #base.accept("network-send", self.sendEventMsg)

  def handle_connect(self):

    """
    Handle connecting to server.
    """
  
    messenger.send("network-connect")
    print "Connected to server..."

    # Client Confirm
    #self.prepareMsg(CLIENT_CONFIRM, CLIENT_SECURITY)

  def handle_close(self):

    """
    Handle closing connection to server.
    """
  
    self.close()
    messenger.send("network-close")
    print "Connection closed."

  def handle_read(self):

    """
    Handle reading data from server.
    """

    # Recieve 1024 bytes of data.
    data = self.recv(1024)

    # Do nothing if there is no data.
    if data <= 0: return None

    # Split data up by line.
    split = data.split("\n")

    # Read data line by line.
    for data in split:

      # Goto next line if no data on this line.
      if not data: continue

      # Get Message ID (the first character).
      msgId = data[0]

      # Get data.
      data = data[1:]

      # Determine what message type and do correct action.

      # Client confirmation (security check).
      if msgId == CLIENT_CONFIRM:

        # SECURITY STRING
        cTime = math.ceil(time.time())
        h = hashlib.new('ripemd160')
        h.update(str(cTime) + "_" + str(CLIENT_VERSION) + "_BumpNBrawl_SuperSecret#ChompR0x")

        CLIENT_SECURITY = h.hexdigest()
      
        self.prepareMsg(CLIENT_CONFIRM, CLIENT_SECURITY)

      # Unregonized message type.
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

# Functions for disconnecting and connecting to server.

client = None
def connectToServer(host):
  client = networkHandler(host, 31592)    
  taskMgr.add(doNetworkUpdate, "NetworkLoop")

def disconnect():

  taskMgr.remove("NetworkLoop")
  try:
    client.close()
  except:
    return None

  
