import actions

class specials(actions.actions):

  """
  Loads up the character special abilitiy.
  """

  def chompy_special(self, task = None):

    """
    Chompy's special ability. Plays animation and waits '.5'
    seconds, then pushes Chompy forward.
    """

    if not task:

      # If special is cooling down.
      if self.player.specialCooldown: return None

      if abs(self.player.movement[0]) < 4.5 and abs(self.player.movement[1]) < 4.5:
        self.player.moveLock(None, .5)
        self.player.setAnim("special", 0)
        taskMgr.doMethodLater(.5, self.chompy_special, "Player_" + str(self.player.id) + "_Action_Special")
      return None
    else:
      self.player.isKnockback = False
      if self.player.movement == [0,0]:
        self.player.setMovement(self.player.power * .65, True, False)
        self.player.setSpecialCooldown()
    
      return task.done

