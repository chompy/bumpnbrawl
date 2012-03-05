from PIL import Image, ImageDraw
from panda3d.core import NodePath, Texture
import ConfigParser, os, math

class mapLoader:

  def __init__(self, mapFile):

    """
    Loads and displays map files.
    """

    # Load config file containing tile data.
    self.tileData = ConfigParser.ConfigParser()
    self.tileData.read(base.assetPath + "/maps.conf")

    # Set Theme
    self.theme = "hq"

    # Create Node Path
    self.node = NodePath("Map")
    self.node.reparentTo(render)

    self.staticMesh = NodePath("StaticMap")
    self.staticMesh.reparentTo(self.node)

    # Load Block
    self.tile = loader.loadModel(base.assetPath + "/tiles/geometry/cube." + base.tileExt)
    self.tile.clearModelNodes()

    # Load Map File
    self.loadMap(mapFile)

  def loadMap(self, mapFile):

    """
    Open the map file and load it up.
    """

    # Make an array of possible player start points.
    base.playerStart = []

    # Load up tiles from PNG
    image = Image.open(mapFile)
    size = image.size

    # Prepare Tile Array
    self.tiles = []
    base.tilePositions = []
    base.tileCoords = {}

    self.mapSize = (float(size[0]) * 2.0, float(size[1]) * 2.0)

    # Go through each pixel collecting tile data.
    for y in range(size[1]):
      self.tiles.append([])
      for x in range(size[0]):
        
        # Grab RGB value.
        value = image.getpixel( (x,y) )
        # Convert RGB value to HEX        
        hexColor = self.rgb2hex(value[0], value[1], value[2])

        # Grab Tile ID
        try:
          bId = self.tileData.getint("colors", hexColor.lower())
        except:
          bId = 0

        self.tiles[len(self.tiles) - 1].append(bId)

        # Load Block
        self.loadTileBlock(bId, [x, y])

    self.staticMesh.flattenStrong()

  def loadTileBlock(self, bId, pos):

    """
    Loads in a tile block at specified location.
    """  

    # Load up a model for blocks with IDs greater then 0. (0 = No block)
    if bId > 0:

      # Load Other Info

      # Z offset
      try:
        zoffset = self.tileData.getint(str(bId), "zoffset")
      except:
        zoffset = 0

      # Block Height
      try:
        height = self.tileData.getint(str(bId), "height")
      except:
        height = 1            

      # Overlap Tile
      try:
        overlap = self.tileData.getint(str(bId), "overlap")
      except:
        overlap = 0

      # Static Node
      try:
        static = self.tileData.getboolean(str(bId), "static")
      except:
        static = True

      # Solid
      try:
        solid = self.tileData.getboolean(str(bId), "solid")
      except:
        solid = True        

      # Invisible
      try:
        invisible = self.tileData.getboolean(str(bId), "invisible")
      except:
        invisible = False

      # Pickup-able
      try:
        pickup = self.tileData.getboolean(str(bId), "pickup")
      except:
        pickup = False

      if overlap > 0:
        self.loadTileBlock(overlap, pos)

      layerNode = NodePath("LevelTile_" + str(pos[0]) + "_" + str(pos[1]))

      # Special Case: Player Start Point
      if bId == 4:
        base.playerStart.append( (pos[0] * 2.0, pos[1] * 2.0, (zoffset) * 2.0) )

      # No need to continue if invisible.
      if invisible: return True

      for i in range(height):
        # Load Block
        m = NodePath("LevelTileBlock_" + str(pos[0]) + "_" + str(pos[1]) + "_" + str(zoffset + i))
        self.tile.instanceTo(m)
        
        # Load Texture
        texPath = base.assetPath + "/tiles/themes/" + self.theme + "/" + str(bId) + ".png"
        if os.path.exists(texPath):
          tex = loader.loadTexture(texPath)
#          tex.setMagfilter(Texture.FTNearest)
          tex.setMinfilter(Texture.FTLinearMipmapLinear)
          tex.setAnisotropicDegree(2)
          m.setTexture(tex)

        # Set Block Pos       
        m.setPos(pos[0] * 2.0, pos[1] * 2.0, (zoffset + i) * 2.0)

        # Log this position.
        tilePos = m.getPos()

        for i in range(len(tilePos)):
          tilePos[i] = int(math.floor(tilePos[i] / 2.0))

        base.tilePositions.append({
          'id'    : bId,
          'pos'   : tilePos,
          'solid' : solid,
          'static': static,
          'pickup': pickup,
          'node'  : m
        })

        base.tileCoords[str(int(tilePos[0])) + "_" + str(int(tilePos[1])) + "_" + str(int(tilePos[2]))] = base.tilePositions[len(base.tilePositions) - 1] 

        # Reparent Model
        if static: m.reparentTo(layerNode)
        else: m.reparentTo(self.node)

      if static: layerNode.getChildren().reparentTo(self.staticMesh)

  def rgb2hex(self, r, g, b):

    """
    Coverts a RGB color value to HEX
    """

    hexchars = "0123456789ABCDEF"
    return hexchars[r / 16] + hexchars[r % 16] + hexchars[g / 16] + hexchars[g % 16] + hexchars[b / 16] + hexchars[b % 16]
