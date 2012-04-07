from pandac.PandaModules import Point3
import math

class camera:

  def __init__(self, player):

    """
    Handles placing and moving the game camera.
    """

    # Disable mouse.
    base.disableMouse()

    # Make camera look down.
    base.camera.setP(-45)

    # Setup player array
    self.players = []

    # Bind to player.
    self.add(player)

    # Cam loop
    taskMgr.add(self.camLoop, "Camera_FollowPlayer", sort=1)

  def add(self, player):

    """
    Adds a player to be tracked by the camera.
    """
   
    # Define Player
    self.players.append(player)

  def remove(self, player):

    """
    Removes a player from tracking.
    """

    self.players.remove(player)
  
  def camLoop(self, task):

    """
    Start a loop that lets the camera follow the player.
    """

    centerPoint = Point3(0,0,0)
    leftdownPoint = Point3(999999,999999,999999)
    rightupPoint = Point3(0,0,0)

    # No Players
    if len(self.players) <= 0:
      return task.cont

    # Single Player
    elif len(self.players) == 1:
      pos = self.players[0].actor.getPos()
      pos[2] = 30
      pos[1] -= 32
      base.camera.setFluidPos(pos)      

    # Greater than one player.
    else:
      for x in self.players:
        for i in range(len(centerPoint)):

          # Get the two players with the greatest distances on each axis.
          for y in self.players:
            if y == x: continue
            pos1 = x.actor.getPos()
            pos2 = y.actor.getPos()
            if abs(pos1[i] - pos2[i]) > abs(centerPoint[i]):
              centerPoint[i] = abs(pos1[i] - pos2[i])

          # Get the left-bottom(0,0) most player.
          pos = x.actor.getPos()
          if pos[i] < leftdownPoint[i]:
            leftdownPoint[i] = pos[i]

          # Get the right-top most player.
          if pos[i] > rightupPoint[i]:
            rightupPoint[i] = pos[i]

      # Get the distance between the furthest characters
      distance = math.sqrt(((rightupPoint[0] - leftdownPoint[0]) ** 2) + ((rightupPoint[1] - leftdownPoint[1]) ** 2))

      camPos = leftdownPoint + (centerPoint / 2.0)

      camPos[2] = 30 + (distance / 1.5)
        
      camPos[1] -= 30 + (distance * .75)
      base.camera.setFluidPos(camPos)

    # Position Background to follow cam
    if base.background:
      try:
        base.background.setFluidX(base.camera.getX())
        base.background.setFluidY(base.camera.getY() + 35)
      except: base.background = None

      
    return task.cont

