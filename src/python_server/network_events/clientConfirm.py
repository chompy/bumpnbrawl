
"""
Handle client confirmation. (Security Check)
"""

CLIENT_VERSION = 1

import time, math, hashlib
SECURE_STR = "_" + str(CLIENT_VERSION) + "_BumpNBrawl_SuperSecret#ChompR0x"


def clientConfirm(client, data):

  checkPass = False
 
  for i in range(-15,15):
    check_str = str(math.ceil(time.time())) + SECURE_STR
    h = hashlib.new('ripemd160')
    h.update(check_str)
    if h.hexdigest() == data:
      checkPass = True
      break

  if not checkPass:
    print "Client #" + str(client.id) + " failed the security check. (DISCONNECTED)"
    client.close()
  else:
    client.clientConfirm = True
    print "Client #" + str(client.id) + " passed the security check."  
  
