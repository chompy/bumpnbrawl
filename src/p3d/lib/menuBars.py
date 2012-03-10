from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode, NodePathsu

class menuBars(DirectObject):

  """
  Makes a list of selectable items.
  """

  def __init__(self, options):

    self.node = NodePath("MenuBarNode")
