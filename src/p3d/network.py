import asyncore,socket,struct 
from direct.task.TaskManagerGlobal import taskMgr 
from direct.task import Task 

timeout_in_miliseconds=3000

# MESSAGE ID REFERENCE
USERNAME = chr(1)
USERID = chr(2)
POSITION = chr(3)
CHAT = chr(4)


class networkHandler(asyncore.dispatcher):

  def __init__(self, host, port):

    asyncore.dispatcher.__init__(self)

    self.create_socket(socket.AF_INET,socket.SOCK_STREAM) 
    self.connect((host,port))
    self.buffer = ""

    self.name = "Chompy"
    self.id = None

  def handle_connect(self):
    print "Connected to host."

  def handle_close(self):
    self.close()

  def handle_read(self):

    data = self.recv(1024)
    if data <= 0: return None

    msgId = data[0]
    data = data[1:].strip()

    # Send Player Username
    if msgId == USERNAME:
      print "Server is requesting username for %s." % self.name
      self.prepareMsg(USERNAME, self.name)

    # Retrieve User ID
    elif msgId == USERID:
      self.id = int(ord(data))
      print "Recieved ID#%s for player %s." % (str(self.id), self.name)


  def prepareMsg(self, msgType, msg):

    """
    Prepares a message to be sent.
    """

    self.buffer = msgType + msg
    
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

client = networkHandler("localhost", 31592)    
taskMgr.add(doNetworkUpdate, "NetworkLoop")

  
