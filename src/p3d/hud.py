from pandac.PandaModules import CardMaker, TextureStage, NodePath, TransparencyAttrib,TextNode
from direct.interval.LerpInterval import LerpColorScaleInterval, LerpScaleInterval
from direct.showbase.Loader import Loader
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText

HUD_BG = [

  [0.9333333333333333, 0.3098039215686275, 0.3411764705882353],
  [0.3764705882352941, 0.5372549019607843, 0.8705882352941176],  
  [0.2549019607843137, 0.9333333333333333, 0.3843137254901961],
  [0.3058823529411765, 1.0, 0.0],

]

HUD_FG = [

  [1,1,1,1],
  [1,1,1,1],  
  [0,0,0,1],
  [0,0,0,1],

]




HUD_FONT = "04B.egg"

class gameHud(DirectObject):

  def __init__(self):

    """
    Init game Hud.
    """
    self.font = loader.loadFont(base.assetPath + "/fonts/" + HUD_FONT)
    
    self.node = NodePath("GameHud")
    self.node.reparentTo(aspect2d)
    
    self.playerHuds = {}

    for i in base.players:
      taskMgr.doMethodLater(.1 + (float(i.id) / 2.0), self.addPlayer, "Hud_DelayPlayerSnapshoot", extraArgs=[i])

    # Update Hud Positions on window event
    self.accept("window-event", self.windowEvent)

  def addPlayer(self, player):

    """
    Adds a Hud for a specific player.
    """

    self.playerHuds[player.id] = {}

    # Make player take snapshot
    if not player.snapshot:
      snapshot = player.takeSnapshot()

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
    self.playerHuds[player.id]['node'].setTransparency(TransparencyAttrib.MAlpha) 
    self.playerHuds[player.id]['node'].reparentTo(self.node)

    hud1 = CardMaker("PlayerHud_BG")
    hud1.setFrame(-.5,.5,-.21, .21)
    hud1.setColor(HUD_BG[i][0],HUD_BG[i][1],HUD_BG[i][2],1)
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

    # Hud FG Color
    textColor = (HUD_FG[i][0], HUD_FG[i][1], HUD_FG[i][2], HUD_FG[i][3])

    # Player # Text
    OnscreenText(
      text = str(self.playerHuds[player.id]['count']), pos = (-.3, -.07), scale = 0.21, fg=textColor, 
      align=TextNode.ACenter, font=self.font, parent=self.playerHuds[player.id]['node'])

    # Player Resist Text
    self.playerHuds[player.id]['resist'] = OnscreenText(
      text = "20.0", pos = (.11, 0), scale = 0.14, 
      fg=textColor, align=TextNode.ALeft, font=self.font, parent=self.playerHuds[player.id]['node'],
      mayChange=True
    )

    # Player Power Up Text
    self.playerHuds[player.id]['powerup'] = OnscreenText(
      text = "n/a", pos = (.11, -.08), scale = 0.08, 
      fg=textColor, align=TextNode.ALeft, font=self.font, parent=self.playerHuds[player.id]['node'],
      mayChange=True
    )

    # Player Snapshot

    snap_frame = CardMaker("PlayerHud_Snapshot")
    snap_frame.setFrame(-.16,.035,-.096, .104)
    snap_frame.setColor(0.407843137254902,0.407843137254902,0.407843137254902,1)
    snap_frame_node = self.playerHuds[player.id]['node'].attachNewNode(snap_frame.generate())
    snap_frame_node.setTransparency(TransparencyAttrib.MAlpha) 
    self.playerHuds[player.id]['snapshot'] = snap_frame_node

    ts = TextureStage('PlayerHud_Snapshot_TextureStage')
    ts.setMode(TextureStage.MDecal)
    snap_frame_node.setTexture(ts, snapshot)

    # Special Ability Recharge Bar
    sa_bar = CardMaker("PlayerHud_SpecialRecharge")
    sa_bar.setFrame(.17,0,-.075, -.06)
    sa_bar.setColor(1,1,0,1)
    sa_bar_node = self.playerHuds[player.id]['node'].attachNewNode(sa_bar.generate())
    sa_bar_node.setX(-.145)
    sa_bar_node.hide()
    self.playerHuds[player.id]['sa_bar'] = sa_bar_node

    # Get Width/Height
    pos1, pos2 = self.playerHuds[player.id]['node'].getTightBounds()
    width = pos2[0] - pos1[0]
    height = pos2[2] - pos1[2]
    self.playerHuds[player.id]['width'] = width
    self.playerHuds[player.id]['height'] = height

    # Use WindowEvent method to set hud position
    self.windowEvent()

    # When player's resist changes update hud.
    self.accept("Player_" + str(player.id) + "_Resist_UpdateHud", self.updatePlayerResist, [player])
    self.updatePlayerResist(player)

    # When player's power up changes update hud.
    self.accept("Player_" + str(player.id) + "_PowerUp_UpdateHud", self.updatePlayerPowerup, [player])
    self.updatePlayerPowerup(player)    

    # When player uses a special, activate cooldown bar.
    self.accept("Player_" + str(player.id) + "_Hud_SpecialAbilityCooldown", self.updatePlayerCooldown, [player])

    # Fader Lerp
    fadeLerp = LerpColorScaleInterval(self.playerHuds[player.id]['node'], .4, (1,1,1,1), (0,0,0,.1))
    fadeLerp.start()

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

  def updatePlayerResist(self, player):

    """
    Updates a player's resistance stat.
    """

    myHud = self.playerHuds[player.id]
    myHud['resist'].setText(str(player.resist))

  def updatePlayerPowerup(self, player):

    """
    Updates a player's power up.
    """

    myHud = self.playerHuds[player.id]
    # TODO
      
  def updatePlayerCooldown(self, player):

    """
    Sets up player cooldown bar to display time
    remaining.
    """

    myHud = self.playerHuds[player.id]
    myHud['sa_bar'].setScale(0,1,1)
    myHud['sa_bar'].show()
    myHud['snapshot'].setColorScale(1,1,1,.6)
    
    # Scale Lerp
    scaleLerp = LerpScaleInterval(myHud['sa_bar'], base.sa_cooldown, (1,1,1), (0,1,1))
    scaleLerp.start()

    taskMgr.doMethodLater(base.sa_cooldown, self.playerCooldownReset, "Player_" + str(player.id) + "_Hud_CooldownReset", extraArgs=[player])

  def playerCooldownReset(self, player):

    """
    Occurs once the player's cooldown has been
    recharged.
    """

    myHud = self.playerHuds[player.id]
    myHud['sa_bar'].hide()
    myHud['snapshot'].setColorScale(1,1,1,1)    

    
    
