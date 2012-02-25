from pandac.PandaModules import CardMaker, TextureStage, NodePath, TransparencyAttrib
from direct.showbase.DirectObject import DirectObject

HUD_COLORS = [

  [0.9333333333333333, 0.3098039215686275, 0.3411764705882353],
  [0.3764705882352941, 0.5372549019607843, 0.8705882352941176],  
  [0.2549019607843137, 0.9333333333333333, 0.3843137254901961],
  [0.3058823529411765, 1.0, 0.0],

]

class gameHud(DirectObject):

  def __init__(self):

    """
    Init game Hud.
    """

    self.node = NodePath("GameHud")
    self.node.reparentTo(aspect2d)
    
    self.playerHuds = {}

    for i in base.players:
      self.addPlayer(i)

    # Update Hud Positions on window event
    self.accept("window-event", self.windowEvent)

  def addPlayer(self, player):

    """
    Adds a Hud for a specific player.
    """

    self.playerHuds[player.id] = {}

    # Get Player class
    self.playerHuds[player.id]['player'] = player

    # Get Player character name
    self.playerHuds[player.id]['character'] = player.character

    # Get the current count of this player.
    for i in range(len(base.players)):
      if base.players[i] == player:
        self.playerHuds[player.id]['count'] = i + 1
        break

    self.playerHuds[player.id]['node'] = NodePath("Player_" + str(player.id) + "_Hud")
    self.playerHuds[player.id]['node'].reparentTo(self.node)

    hud1 = CardMaker("PlayerHud_BG")
    hud1.setFrame(-.5,.5,-.21, .21)
    hud1.setColor(HUD_COLORS[i][0],HUD_COLORS[i][1],HUD_COLORS[i][2],1)
    hud1_node = self.playerHuds[player.id]['node'].attachNewNode(hud1.generate())
    hud1_node.setTransparency(TransparencyAttrib.MAlpha)

    # Load Textures
    hud_tex = loader.loadTexture(base.assetPath + "/hud/player_hud.png")
    hud_tex2 = loader.loadTexture(base.assetPath + "/hud/player_hud_mask.png")    

    # Texture Stage
    ts = TextureStage('PlayerHud_TextureStage')
    ts.setMode(TextureStage.MDecal)
    hud1_node.setTexture(hud_tex2, 1)
    hud1_node.setTexture(ts, hud_tex)

    self.playerHuds[player.id]['node'].setScale(.45)

    # Get Width/Height
    pos1, pos2 = self.playerHuds[player.id]['node'].getTightBounds()
    width = pos2[0] - pos1[0]
    height = pos2[2] - pos1[2]
    self.playerHuds[player.id]['width'] = width
    self.playerHuds[player.id]['height'] = height

    # Use WindowEvent method to set hud position
    self.windowEvent()

  def windowEvent(self, window = None):
    """
    Update window size info everytime a window event occurs.
    """

    self.winWidth = base.win.getProperties().getXSize() 
    self.winHeight = base.win.getProperties().getYSize()
    self.winAspect = float(self.winWidth) / float(self.winHeight)    

    # Set Positions
    for i in self.playerHuds:
      count = self.playerHuds[i]['count']
      
      # Get X and Y
      x = -1
      y = 0
      for z in range(count):
        x += 1
        if x > 1:
          x = 0
          y += 1

      # Set Position
      self.playerHuds[i]['node'].setPos(
        (-self.winAspect + .05 + (self.playerHuds[i]['width'] / 2.0)) + (x * ((self.winAspect * 2.0) - self.playerHuds[i]['width'] - .1 )), 0, (.95 - (self.playerHuds[i]['height'] / 2.0)) - (y * 1.725)
      )
      
