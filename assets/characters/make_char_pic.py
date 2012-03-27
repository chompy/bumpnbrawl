import sys, os
from direct.actor.Actor import Actor
from pandac.PandaModules import Texture, Camera, NodePath, OrthographicLens, TransparencyAttrib

# ShowBase
import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase

if len(sys.argv) <= 1:
  print "ERROR: You must specify a character."
  sys.exit()

character = sys.argv[1]
if not os.path.exists("./" + character):
  print "ERROR: Character does not exists."
  sys.exit()

actor = Actor("./" + character + "/model.egg", {'idle' : "./" + character + "/model-idle.egg"})
actor.reparentTo(render)
actor.pose("idle", 5)
actor.setH(60)

# Width and Height
width = 512
height = 512

# Make a buffer.
tex=Texture()
mybuffer = base.win.makeTextureBuffer('HDScreenShotBuff',width,height,tex,True)

# Make a new camera.
cam=Camera('SnapshotCam') 

lens = OrthographicLens()
lens.setFilmSize(7.0, 15)

cam.setLens(lens) 
cam.getLens().setAspectRatio(width/height) 

pCam=NodePath(cam) 
  
mycamera = base.makeCamera(mybuffer,useCamera=pCam)
mycamera.setX(15)    
mycamera.setZ(0)
mycamera.setY(-15) 

mycamera.lookAt(actor)

# Set scene related stuff     
myscene = actor
mycamera.node().setScene(myscene) 

# Generate a image.
base.graphicsEngine.renderFrame()
tex = mybuffer.getTexture() 
mybuffer.setActive(False) 
snapshot = tex
base.graphicsEngine.removeWindow(mybuffer)
snapshot.write("./" + character + "/picture.jpg")
print "SUCCESS!"
