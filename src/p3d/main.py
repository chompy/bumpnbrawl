# Import Panda3D Modules
import direct.directbase.DirectStart
from pandac.PandaModules import loadPrcFileData, VBase4
from direct.showbase.ShowBase import ShowBase

# Panda3d Config
base.setFrameRateMeter(True)
loadPrcFileData("", "sync-video #f")

# Import game specific modules
import mapLoader, player, camera

# Path to game assets.
base.assetPath = "../../assets"

# Ext to use when loading tiles.
base.tileExt = "egg"

# Ext to use when loading character.
base.charExt = "egg"

# Make Background Color Black
base.win.setClearColorActive(True)
base.win.setClearColor(VBase4(0, 0, 0, 1))

CONTROL1 = {
  'left'    :   'arrow_left',
  'right'   :   'arrow_right',
  'up'      :   'arrow_up',
  'down'    :   'arrow_down',
  'btn1'    :   'shift',
  'btn2'    :   'z'
}

CONTROL2 = {
  'left'    :   'a',
  'right'   :   'd',
  'up'      :   'w',
  'down'    :   's',
  'btn1'    :   'q',
  'btn2'    :   'e'
}

class ChompinBomper(ShowBase):

  def __init__(self):

    """
    Init ze game!
    """

    self.map = mapLoader.mapLoader(base.assetPath + "/maps/chomp_map1.PNG")

    base.playerid = 0
    base.players = []
    base.players.append(player.player("chompy", True, CONTROL1))
    base.players.append(player.player("cuby", True, CONTROL2))

    self.camera = camera.camera(base.players[0])
    self.camera.add(base.players[1])

    run()

ChompinBomper()
