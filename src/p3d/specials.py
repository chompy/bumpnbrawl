import actions
from direct.interval.LerpInterval import LerpColorScaleInterval

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
        self.player.particlePlay("powerup", .5)
        taskMgr.doMethodLater(.5, self.chompy_special, "Player_" + str(self.player.id) + "_Action_Special")
      return None
    else:
      self.player.isKnockback = False
      if self.player.movement == [0,0]:
        self.player.setMovement(self.player.power * 1.75, True, False)
        self.player.setSpecialCooldown()
    
      return task.done

  def renoki_special(self, task = None):

    """
    Renoki's special ability. Pushes Renoki forward and ignores some
    collisions.
    """

    if not task:

      # If special is cooling down.
      if self.player.specialCooldown: return None

      self.player.moveLock(None, .25)
      self.player.setAnim("special", 0, 0, 20)      
      self.player.setAnim("special", 1)
      self.player.particlePlay("powerup", .25) 
      taskMgr.doMethodLater(.25, self.renoki_special, "Player_" + str(self.player.id) + "_Action_Special")

      lerp = LerpColorScaleInterval(self.player.actor, .3, (1,1,1,.5), (1,1,1,1))
      lerp.start()
      
      return None
    else:

      if self.player.direction[0] and not self.player.direction[1]:
        self.player.particlePlay("speed-left", 1.25)
      elif self.player.direction[1] and not self.player.direction[0]:
        self.player.particlePlay("speed-up", 1.25)
      else:
        self.player.particlePlay("speed-diag", 1.25)
        
      self.player.isKnockback = False
      self.player.setMovement(20.0, True, False)
      self.player.noCollide = 1
      self.player.setSpecialCooldown()

      taskMgr.doMethodLater(1.25, self.renoki_reset, "Player_" + str(self.player.id) + "_Action_SpecialReset")

  def renoki_reset(self, task = None):

    lerp = LerpColorScaleInterval(self.player.actor, .3, (1,1,1,1), (1,1,1,.5))
    lerp.start()    
    self.player.setAnim("special", 0, 20, None) 
    self.player.noCollide = None
      

