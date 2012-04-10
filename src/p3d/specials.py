import actions
from direct.interval.LerpInterval import LerpColorScaleInterval
from pandac.PandaModules import Vec3

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

      # Play activate sound
      self.player.sfx['special'].play()

      if abs(self.player.movement[0]) < 4.5 and abs(self.player.movement[1]) < 4.5:
        self.player.moveLock(None, .5)
        self.player.setAnim("special", 0)        
        self.player.particlePlay("powerup", .5)
        taskMgr.doMethodLater(.5, self.chompy_special, "Player_" + str(self.player.id) + "_Action_Special")
      return None
    else:
      self.player.isKnockback = False
      if self.player.movement == [0,0]:
        self.player.setMovement(self.player.power * 1.25, True, False)
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

      # Play activate sound
      self.player.sfx['special'].play()

      self.player.moveLock(None, .25)
      self.player.setAnim("special", 0, 0, 20)      
      self.player.setAnim("special", 1)
      self.player.particlePlay("powerup", .25) 
      taskMgr.doMethodLater(.25, self.renoki_special, "Player_" + str(self.player.id) + "_Action_Special")

      lerp = LerpColorScaleInterval(self.player.actor, .3, (1,1,1,.5), (1,1,1,1))
      lerp.start()
      
      return None
    else:
        
      p = self.player.particlePlay("speed", 1.25, True)

      if self.player.direction[0] and not self.player.direction[1]:
        p.getParticlesList()[0].renderer.setNonanimatedTheta(90.0)
      elif self.player.direction[0] > 0 and self.player.direction[1]:
        p.getParticlesList()[0].renderer.setNonanimatedTheta(-45.0)
      elif self.player.direction[0] < 0 and self.player.direction[1]:
        p.getParticlesList()[0].renderer.setNonanimatedTheta(45.0)
                
      self.player.isKnockback = False
      self.player.setMovement(15.0, True, False)
      self.player.noCollide = 1
      self.player.setSpecialCooldown()

      taskMgr.doMethodLater(1.25, self.renoki_reset, "Player_" + str(self.player.id) + "_Action_SpecialReset")

  def renoki_reset(self, task = None):

    lerp = LerpColorScaleInterval(self.player.actor, .3, (1,1,1,1), (1,1,1,.5))
    lerp.start()    
    self.player.setAnim("special", 0, 20, None) 
    self.player.noCollide = None


  def hawk_special(self, task = None):

    """
    Hawk's special ability. A Super punch.
    """      

    if not task:

      # If special is cooling down.
      if self.player.specialCooldown: return None

      # Play activate sound
      self.player.sfx['special'].play()

      self.player.moveLock(None, 1.5)
      self.player.setAnim("special", 0, 0, 50)      
      self.player.particlePlay("powerup", .25)   

      taskMgr.doMethodLater(1.35, self.hawk_special, "Player_" + str(self.player.id) + "_Action_Special")
      taskMgr.doMethodLater(1.15, self.hawk_punch_play, "Player_" + str(self.player.id) + "_Action_PunchParticles", extraArgs=[])    

    else:

      self.player.setSpecialCooldown()

      hitRange = 3
     
      for i in base.players:
        if i == self.player: continue
        tilePos = i.getTilePos()          
        for x in range(0, hitRange):
          myTile = self.player.getTilePos()
          for y in range(len(self.player.direction)):
            myTile[y] += float(x) * self.player.direction[y]
 
          if myTile == tilePos:

            power = (self.player.power * 2.0) - (i.resist * 1.5)

            i.ode_body.setLinearVel(self.player.direction[0] * power, self.player.direction[1] * power, 0)
            i.reduceResist()
            
            break

        

      return task.done

  def hawk_punch_play(self):

    """
    Play Hawk's punch particle effect.
    """
    
    p = self.player.particlePlay("punch", .5, True)
    p.getParticlesList()[0].emitter.setOffsetForce(Vec3(self.player.direction[0] * 4.0, self.player.direction[1] * 4.0, 0.0000))  
