from pandac.PandaModules import ButtonThrower 

class Interface(object): 
   def getButton(self,key): 
      '''returns true if the button is pressed, key is same as the key events''' 
      return (key in self._butList) 
   def getButtonHit(self,key): 
      '''reuturns true if the button was pushed this frame, key is same as the key events''' 
      return (key in self._butHitList) 
   def buttonsPressed(self): 
      '''returns a list of all buttons being pressed''' 
      return self._butList 
   def getMouse(self,key): 
      '''same as getButton but for mouse buttons. key is one of left,middle,right,wheel''' 
      if key=='wheel': return self._wheel #wheel special... 
      return (key in self._mButList) 
   def getMouseHit(self,key): 
      '''same as getButtonhit but for mouse.  key is one of left,middle,right,wheel'''
      return (key in self._mButHitList) 
   def mousePressed(self): 
      '''same as buttonsPressed- but does not include the wheel...''' 
      return self._mButList 
   def getMousePos(self): 
      '''the x,y mouse position according to render2d''' 
      return [self._mPos[0],self._mPos[1]] 
   def getMousePixel(self): 
      '''the x,y pixel under mouse...0-screenWidth,0-screenHeight from upper left corner''' 
      return [self._mPos[2],self._mPos[3]] 
   def getMouseAspect(self): 
      '''the x,y mouse position according to aspect2d''' 
      return [self._mPos[4],self._mPos[1]] 
   def getMouseSpeed(self): 
      '''the delta x,delta y of the mouse pos in pixel coords...(everything else 
         has both positive and negative which messes up speed and direction)''' 
      return [self._mPos[2]-self._mPosOld[2],self._mPos[3]-self._mPosOld[3]]      
    
   def __init__(self):        
      #base.disableMouse() 

      #make sure we don't override the normal events... 
      mw = base.buttonThrowers[0].getParent() 
      self.buttonThrower = mw.attachNewNode(ButtonThrower('Polling Buttons')) 
      self.buttonThrower.node().setPrefix('poll-') 
             
      #mouse buttons 
      self._mPos = [0,0,0,0,0] 
      self._mPosOld = [0,0,0,0,0] 
      self._mButList = [] 
      self._mButHitList = [] 

      base.accept('poll-mouse1',self._setmBut,['left',1]) 
      base.accept('poll-mouse3',self._setmBut,['right',1]) 
      base.accept('poll-mouse2',self._setmBut,['middle',1]) 

      base.accept('poll-mouse1-up',self._setmBut,['left',0]) 
      base.accept('poll-mouse3-up',self._setmBut,['right',0]) 
      base.accept('poll-mouse2-up',self._setmBut,['middle',0]) 

      #wheel is special... 
      self._wheel = 0 
      base.accept('poll-wheel_up',self.__setattr__,['_wheel',-1]) 
      base.accept('poll-wheel_down',self.__setattr__,['_wheel',1]) 

      #keyboard buttons 
      self._but =['a','b','c','d','e','f','g','h','i','j','k', 
               'l','m','n','o','p','q','r','s','t','u','v', 
               'w','x','y','n','z', 
               '`','0','1','2','3','4','5','6','7','8','9','-','=', 
               '[',']','\\',';',"'",',','.','/',              #note that \\ is the \ key...stupid python      
               'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12', 
               'escape','scroll_lock', 
               'backspace','insert','home','page_up','num_lock', 
               'tab','delete','end','page_down', 
               'caps_lock','enter','arrow_left','arrow_up','arrow_down','arrow_right',
               'shift','lshift','rshift', 
               'control','lcontrol','rcontrol','alt','lalt','ralt','space' 
               ] 
      for key in self._but: 
         base.accept('poll-'+key,self._setBut,[key,1]) 
         base.accept('poll-'+key+'-up',self._setBut,[key,0]) 
      self._butList = [] 
      self._butHitList = [] 
      #print screen is different, only has up...put it into hit list when released 
      base.accept('poll-print_screen-up',self._butHitList.append,['print_screen']) 

      taskMgr.add(self._updateMouse,'update Mouse Coordinates',priority=-49)    #right after dataloop 
      taskMgr.add(self._updateKeys,'update Key Hits',priority=-60)    #before everything else 


   def _setBut(self,key,val): 
      if val==1: 
         self._butList.append(key) 
         self._butHitList.append(key) 
      else: 
         try: self._butList.remove(key) 
         except ValueError: pass    #missed the keyDown event, happens if program hiccups when key is pushed 
          
   def _setmBut(self,key,val): 
      if val==1: 
         self._mButList.append(key) 
         self._mButHitList.append(key) 
      else: 
         try: self._mButList.remove(key) 
         except ValueError: pass 
                
   def _updateMouse(self,task): 
      if base.mouseWatcherNode.hasMouse(): 
         self._mPosOld = self._mPos 
         self._mPos = [0,0,0,0,0] 
         self._mPos[0] = base.mouseWatcherNode.getMouseX() 
         self._mPos[1] = base.mouseWatcherNode.getMouseY() 
         #pixel coordinates 
         self._mPos[2]=base.win.getPointer(0).getX() 
         self._mPos[3]=base.win.getPointer(0).getY() 
         #aspect2d coordinates (mPos[4],mPos[1] 
         self._mPos[4]=self._mPos[0]*base.getAspectRatio() 
      else: self._mPosOld = self._mPos    #out of screen, dx,dy=0 
       
      return task.cont 
    
   def _updateKeys(self,task): 
      self._butHitList = [] 
      self._mButHitList = [] 
      self._wheel = 0 
      return task.cont 
    
   #allows only 1 copy (singleton)    
   def __new__(cls,*args, **kwargs): 
      if '_inst' not in vars(cls): 
         cls._inst = super(Interface,cls).__new__(cls,*args,**kwargs) 
      return cls._inst 

