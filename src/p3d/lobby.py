# Import Panda3D Modules
import sys, os, math
from pandac.PandaModules import loadPrcFileData, TextNode, NodePath, CardMaker,TextureStage, Texture, VBase3, TransparencyAttrib, WindowProperties, TextProperties, TextPropertiesManager
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpHprInterval
from panda3d.core import loadPrcFile
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.fsm.FSM import FSM
from direct.interval.LerpInterval import LerpColorScaleInterval, LerpPosHprScaleInterval, LerpHprInterval
from direct.interval.MetaInterval import Sequence

from lib import menuBars, menuOptions, inputHelp
import gameInput

loadPrcFile("../../assets/Config.prc")

# ShowBase
import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase

# Path to game assets.
base.assetPath = "../../assets"

# Ext to use when loading tiles.
base.tileExt = "egg"

# Ext to use when loading character.
base.charExt = "egg"

# Load Character List
charDir = os.listdir(base.assetPath + "/characters")
charList = []
for i in charDir:
  if os.path.isdir(base.assetPath + "/characters/" + i):
    charList.append(i)

charData = []
for i in charList:
  data = {}

  # Load Name from external file
  name = "None"
  if os.path.exists(base.assetPath + "/characters/" + i + "/name.txt"):
    name = open(base.assetPath + "/characters/" + i + "/name.txt", "r").read()

  # Load stats from external file...
  moveSpeed = 1.0
  power = 1.0
  resist = 1.0
  if os.path.exists(base.assetPath + "/characters/" + i + "/stats.txt"): 
    statFile = open(base.assetPath + "/characters/" + i + "/stats.txt").read().split("\n")
    moveSpeed = float(statFile[0].split(" ")[0])
    power = float(statFile[1].split(" ")[0])
    resist = float(statFile[2].split(" ")[0])

  data['name'] = name.strip()
  data['speed'] = moveSpeed
  data['power'] = power
  data['resist'] = resist
  data['picture'] = base.assetPath + "/characters/" + i + "/picture.jpg"
  charData.append(data)

base.playerProfiles = []

# Character Select Col Size
CHAR_COL_SIZE = 5

class gameLobby(FSM):

  def __init__(self):

    # Init FSM
    FSM.__init__(self, 'MenuFSM')

    # Disable Mouse
    base.disableMouse()

    # Load Fonts
    self.boldFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansBold.ttf")
    self.regFont = loader.loadFont(base.assetPath + "/fonts/DejaVuSansCondensed.ttf")
    self.pixelFont = loader.loadFont(base.assetPath + "/fonts/04B.egg")

    # Lobby node
    self.node = NodePath("LobbyNode")
    self.node.reparentTo(render)     

    self.node2d = NodePath("Lobby2DNode")
    self.node2d.reparentTo(aspect2d)

    # Prepare menu BG
    menu_frame = CardMaker("Menu_Background")
    menu_frame.setFrame(-4,4,-4,4)
    menu_frame.setColor(0.3843137254901961, 0.8509803921568627, 0.6117647058823529,1)
    menu_frame_node = self.node.attachNewNode(menu_frame.generate())
    menu_frame_node.setY(8)

    bgTex = loader.loadTexture(base.assetPath + "/menu/bg_overlay.png")

    bgTex.setWrapU(Texture.WMRepeat)
    bgTex.setWrapV(Texture.WMRepeat)

    #menu_frame_node.setTexture(bgTex)

    ts = TextureStage('PlayerHud_Snapshot_TextureStage')
    ts.setMode(TextureStage.MDecal)
    menu_frame_node.setTexture(ts, bgTex)    

    lerper = NodePath("Menu_Background_Lerper")
    menu_frame_node.setTexProjector(ts, NodePath(), lerper)
    menu_lerp = lerper.posInterval(60, VBase3(-1, 1, 0))
    menu_lerp.loop()

    # Window Object
    self.windowObj = []    

    # MENU ASSETS
    # ===================

    # Menu Bar
    self.menuBar = menuBars.menuBars([])
    self.menuBar.node.setZ(.7)

    # Menu Title
    TITLE = OnscreenImage(image = base.assetPath + "/menu/title_gamelobby.png", pos = (0, 0, .8), scale=(.5), parent=self.node2d)
    TITLE.setTransparency(TransparencyAttrib.MAlpha)
    self.addWindowNode(TITLE, -1, .5)

    # Sidebar
    SIDEBAR = OnscreenImage(image = base.assetPath + "/menu/lobby_sidebar.png", pos = (0, 0, 0), scale=(1.5), parent=self.node2d)
    SIDEBAR.setTransparency(TransparencyAttrib.MAlpha)
    self.addWindowNode(SIDEBAR, 1, -1.5)

    # Seperators
    charSelect = OnscreenText(text = 'character select', pos = (0, .575), scale = .065, shadow=(.1,.1,.1,.5), fg=(1,1,1,1), font=self.pixelFont, align=TextNode.ALeft, parent=self.node2d)
    self.addWindowNode(charSelect, -1, .1)

    # Show Characters
    x = 0
    y = 0

    self.charSelect = NodePath("CharacterSelectPortraits")
    self.charSelect.reparentTo(self.node2d)
    self.addWindowNode(self.charSelect, -1, .3)
    self.charSelect.setZ(.4)

    base.charSlots = []
    for i in charData:

      port = characterPortrait(i['picture'])
      port.reparentTo(self.charSelect)

      port.setScale(.125)
      port.setPos((x * .25), 0, (y * -.25))

      base.charSlots.append(port)

      # Increment
      x += 1
      if x > CHAR_COL_SIZE:
        x = 0
        y += 1

    # Player Profiles
    self.playerProfiles = NodePath("PlayerProfiles")
    self.playerProfiles.reparentTo(self.node2d)
    self.addWindowNode(self.playerProfiles, 1, -.65)
    self.playerProfiles.setZ(.865)

    self.playerSlots = []

    for i in range(8):
    
      pp = playerProfile(i + 1)
      pp.reparentTo(self.playerProfiles)

      pp.setZ(i * -.25)

      self.playerSlots.append(pp)


    # Bind Window Event
    self.windowEvent()  
    self.accept("window-event", self.windowEvent)    

  def addWindowNode(self, node, side, xoffset):

    """
    Add NodePath to list of nodes that will be
    repositioned everytime the window is resized.
    """
     
    self.windowObj.append([node, side, xoffset])

  def rmWindowNode(self, node):

    """
    Remove NodePath from above list.
    """

    for i in self.windowObj:
      if i[0] == node:
        self.windowObj.remove(i)
        break

  def windowEvent(self, window = None):

    """
    Update window size info everytime a window event occurs.
    """

    self.winWidth = base.win.getProperties().getXSize() 
    self.winHeight = base.win.getProperties().getYSize()
    self.winAspect = float(self.winWidth) / float(self.winHeight)  

    # Update Node
    for i in self.windowObj:
      i[0].setX((self.winAspect * i[1]) + i[2])    

# The following handles the portraits for each character...
PORTRAIT_BG = base.assetPath + "/menu/character_portrait_bg.png"
PORTRAIT_BG_SELECTED = base.assetPath + "/menu/character_portrait_bg_selected.png"
class characterPortrait(NodePath):

  def __init__(self, char_image):

    NodePath.__init__(self, "CharacterPortrait")

    self.pixelFont = loader.loadFont(base.assetPath + "/fonts/04B.egg")
    
    self.bg = OnscreenImage(image = PORTRAIT_BG, pos = (0, 0, 0), scale=(1), parent=self)
    self.bg.setTransparency(TransparencyAttrib.MAlpha)

    self.bg_selected = OnscreenImage(image = PORTRAIT_BG_SELECTED, pos = (0, 0, 0), scale=(1), parent=self)
    self.bg_selected.setTransparency(TransparencyAttrib.MAlpha)  
    self.bg_selected.hide()  

    self.char_image = char_image
    self.char = OnscreenImage(image = char_image, pos = (0, 0, 0), scale=(.68), parent=self)

    self.text = []
    for i in range(4):
      x = i % 2
      y = int(math.floor(i / 2))
      
      self.text.append(
        OnscreenText(text = str(i + 1), pos = ( -.3 + (x * .66), y * -.55), scale = .8, shadow=(.1,.1,.1,.5), fg=(1,1,1,1), font=self.pixelFont, align=TextNode.ACenter, parent=self)
      )
      self.text[i].hide()

  def select(self):
    self.bg.hide()
    self.bg_selected.show()

  def unselect(self):
    self.bg.show()
    self.bg_selected.hide()

  def setNumber(self, number, show=True):

    if show:
      self.text[number - 1].show()
    else:
      self.text[number - 1].hide()

  def hideNumber(self):
    self.text.hide()

  def setImage(self, char_image):
    self.char_image = char_image
    self.char.setImage(char_image)

# The Following handles the loading of player profiles...
base.playerProfileSelector = []
class playerProfile(NodePath):

  def __init__(self, slotNo = 1):
    NodePath.__init__(self, "Player" + str(slotNo) + "Profile")

    base.playerProfileSelector.append(self)

    self.state = 0
    self.player = -1

    self.pixelFont = loader.loadFont(base.assetPath + "/fonts/04B.egg")

    self.pNumText = OnscreenText(text = str(slotNo), pos = (.55, -.1), scale = .35, fg=(.745,.745,.745,.7), font=self.pixelFont, align=TextNode.ACenter, parent=self)   

    # Press Button to Join State
    self.joinText = OnscreenText(text = "press button 1\nto join.", pos = (0, 0), scale = .07, fg=(.694,.031,.031,1), font=self.pixelFont, align=TextNode.ALeft, parent=self)
    self.joinText.hide()

    # Profile Select State
    self.profileSelect = NodePath("ProfileSelect")
    self.profileSelect.reparentTo(self)
    self.profileSelect.hide()

    profileText = OnscreenText(text = "profile", pos = (0, .025), scale = .1, fg=(.694,.031,.031,1), font=self.pixelFont, align=TextNode.ALeft, parent=self.profileSelect)
    self.profileName = OnscreenText(text = "< guest >", pos = (.25, -.065), scale = .1, fg=(1,1,1,1), font=self.pixelFont, align=TextNode.ACenter, parent=self.profileSelect)    

    # Character Select State
    self.charSelect = NodePath("CharacterSelect")
    self.charSelect.reparentTo(self)
    self.charSelect.hide()

    self.pPortrait = characterPortrait(charData[0]['picture'])
    self.pPortrait.setScale(.08)
    self.pPortrait.setPos(.06,0,-.04)
    self.pPortrait.reparentTo(self.charSelect)
    self.playerName = OnscreenText(text = "guest", pos = (0, .08), scale = .05, fg=(.694,.031,.031,1), font=self.pixelFont, align=TextNode.ALeft, parent=self.charSelect)
    self.charName = OnscreenText(text = "chompy", pos = (0, .045), scale = .04, fg=(1,1,1,1), font=self.pixelFont, align=TextNode.ALeft, parent=self.charSelect)   

    self.showNextJoinProfile()

    self.charSelected = 0

  def showNextJoinProfile(self):
  
    # See if this one should display Join text 
    hasOne = False
    for i in base.playerProfileSelector:
      if i.state == 0 and not hasOne: 
        i.joinText.show()
        hasOne = True

        # Accept Player Input
        
        for x in range(4):
          isOK = False
          for y in base.playerProfileSelector:
            if y.player == x + 1: 
              isOK = True
              break

          if not isOK:
            base.accept("p" + str(x + 1) + "_btna", i.selectProfile, [x + 1])
      else:
        i.joinText.hide()

  def cancelPlayer(self):
    self.player = -1
    self.state = 0

    self.joinText.show()
    self.charSelect.hide()
    self.profileSelect.hide()

    self.showNextJoinProfile()

  def selectProfile(self, playerNo = None):
    profile = "guest"

    # Set Player Number
    self.player = playerNo
    self.visibleNumber = 0
    for i in base.playerProfileSelector:
      self.visibleNumber += 1 
      if i == self: break

    # Unselect character slot
    base.charSlots[self.charSelected].setNumber(self.visibleNumber, False)
    stillSelected = False
    for i in base.playerProfileSelector:
      if i == self: continue
      if i.charSelected == self.charSelected and i.state == 2: 
        stillSelected = True

    if not stillSelected:
      base.charSlots[self.charSelected].unselect()
          
    base.accept("p" + str(playerNo) + "_btna", self.selectCharacter, [profile])
    base.accept("p" + str(playerNo) + "_btnb", self.cancelPlayer)

    base.ignore("p" + str(self.player) + "_left")
    base.ignore("p" + str(self.player) + "_right")
    base.ignore("p" + str(self.player) + "_up")
    base.ignore("p" + str(self.player) + "_down")    
    
    self.state = 1
               
    self.showNextJoinProfile()

    self.joinText.hide()
    self.charSelect.hide()
    self.profileSelect.show()        

  def selectCharacter(self, profile):
    self.state = 2

    base.accept("p" + str(self.player) + "_btnb", self.selectProfile, [self.player])  

    base.accept("p" + str(self.player) + "_left", self.updateCharSelectGrid, [-1])
    base.accept("p" + str(self.player) + "_right", self.updateCharSelectGrid, [1])
    base.accept("p" + str(self.player) + "_up", self.updateCharSelectGrid, [-CHAR_COL_SIZE])
    base.accept("p" + str(self.player) + "_down", self.updateCharSelectGrid, [CHAR_COL_SIZE])

    self.updateCharSelectGrid(0)
  
    self.charSelect.show()

    self.joinText.hide()
    self.profileSelect.hide()

  def updateCharSelectGrid(self, select):

    select = self.charSelected + select

    if select > len(base.charSlots) - 1:
      select = 0

    if select < 0: select = len(base.charSlots) - 1
      

    stillSelected = False
    for i in base.playerProfileSelector:
      if i == self: continue
      if i.charSelected == self.charSelected and i.state == 2: 
        stillSelected = True

    if not stillSelected:
      base.charSlots[self.charSelected].unselect()

    base.charSlots[self.charSelected].setNumber(self.visibleNumber, False)
    self.charSelected = select
    base.charSlots[self.charSelected].select()
    base.charSlots[self.charSelected].setNumber(self.visibleNumber, True)

    self.pPortrait.setImage(charData[self.charSelected]['picture'])
    self.charName.setText(charData[self.charSelected]['name'].lower())

gameInput.gameInput() 
m = gameLobby()
#m.request("Title")
run()
