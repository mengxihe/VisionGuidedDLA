__author__ = "GSK"

import Rhino.Geometry as rg
import math
import random
import time
#from time import sleep


#__INIT__


currPos = iPosition
glichTresh = iGlitchTreshold
positions = []
#lastPos = rg.Point3d(0.0,0.0,0.0) #initial position may be middle of the frame


class GetVector:
    def __init__(self, pos, delay):
        
        self.CurrPosition = rg.Point3d(pos.X,pos.Y,pos.Z)
        self.LastPosition = rg.Point3d(0.0,0.0,0.0)
        self.HistoryOfPoints = []
        self.HistoryOfPoints.append(self.CurrPosition)
        self.Vector = rg.Vector3d(0.0,0.0,0.0)
        
        self.Delay = delay #magic happends here
        
    def Update(self,pos):
        
        #pos = Smooth(pos,tresh)
        
        self.Vector = rg.Vector3d(self.CurrPosition - self.LastPosition)
        self.LastPosition = self.CurrPosition
        self.CurrPosition = pos 
        
        self.HistoryOfPoints.append(self.CurrPosition)
        time.sleep(self.Delay)
        
        if len(self.HistoryOfPoints)>10:
            del self.HistoryOfPoints[0]
            
        return self.Vector
        return Smooth(self.Vector,glichTresh)
        
    def Smooth(self,val,tresh):
        pass
        av = mean(self.HistoryOfPoints)
        
        
        if abs(val - av) > tresh:
            val = av
        
        return val



#__MAIN__

if iReset or not("a" in globals()):
    a = GetVector(currPos,0.1)
else:
    vec = a.Update(currPos)