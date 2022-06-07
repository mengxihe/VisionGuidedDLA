__author__ = "GSK"

import Rhino.Geometry as rg
import random
import math

#__External_Values_Order__
brchList = iBrch
startingPoint = iCenter
maxRad = iMaxRad
shortening = iRadShort
mode = iMode
#tol = iTolerance
tol = 1.0                 #this is a bad practice to hardcode value but for now it works

#__Empty_Lists_Creation__
stPtList = []
endPtList = []
allPtList = []
vecList = []
stPlList = []
endPlList = []

distList1 = []
distList2 = []

outGeo = []
newGeo = []

def GetBranchInfo(branchList,rootPoint):
    #this method do the heavy lifting and is the main one
    branchTupleList = []
    
    biggestDist = 1.0                       #starting distance to be updated later on
    startPt = rg.Point3d(0,0,0)             #initial values
    endPt = rg.Point3d(0,0,0)
    
    actualSize = rg.Interval(0.0,11.0) # to be updated each time
    #desiredSize = rg.Interval(0.05,1.0) 
    desiredSize = rg.Interval(maxRad*shortening,maxRad)
    
    #__Main_Loop_
    for branch in branchList:
        
        #_Point_creation
        startPt = branch.From
        endPt = branch.To
        
        stPtList.append(startPt)
        endPtList.append(endPt)
        allPtList.append(startPt)
        allPtList.append(endPt)
        #print startPt, endPt
        
        #_DirectionVector_creation
        lineForVector = rg.Line(startPt, endPt)
        DirectionVector = lineForVector.Direction
        vecList.append(DirectionVector)
        
        #_Planes_creation
        stPlane = rg.Plane(startPt, lineForVector.Direction)
        endPlane = rg.Plane(endPt, lineForVector.Direction)
        stPlList.append(stPlane)
        endPlList.append(endPlane)
        
        ##__Distance_Calculation_->_Radius_Calculation
        dist1 = GetDistance(startPt,rootPoint)
        dist2 = GetDistance(endPt,rootPoint)
        #dist1 = startPt.DistanceTo(rootPoint)
        #dist2 = endPt.DistanceTo(rootPoint)
        
        #_size_check___maybe_to_be_moved
        if dist1 > biggestDist:
            biggestDist = dist1
        if dist2 > biggestDist:
            biggestDist = dist2
        actualSize.Grow(biggestDist)        #this should update Interval to include the number
        
        distList1.append(dist1)
        distList2.append(dist2)
        
        ##__Radius_Caluclation
        rad1 = RemapValue(dist1,actualSize,desiredSize,False)
        rad2 = RemapValue(dist2,actualSize,desiredSize,False)
        print rad1, rad2
        
        ##__Working_Part_Geometry_creation
        #tube = GetMeshTube(startPt,endPt,DirectionVector,rad1,rad2)
        tube=getClosedB(startPt,endPt,DirectionVector,rad1,rad2)
        #tube = GetMeshTube(startPt,endPt,DirectionVector,0.6,0.5)
        sphere = GetMeshSphere(endPt,rad2)
        
        outGeo.append(tube)
        outGeo.append(sphere)
        #print outGeo
        
        #_Tuple_creation
        branchTuple =(startPt,endPt,DirectionVector,stPlane,endPlane)
        branchTupleList.append(branchTuple)
        #print branchTuple
    
    newGeo = rg.Brep.CreateBooleanUnion(outGeo, tol)
    return branchTupleList
    

if mode == 0:
    def RemapValue(val, source, target, clip):
        # val is float, source and target Intervals, clip boolean
        value = val 
        sourceMin = source.Min
        sourceMax = source.Max
        targetMin = target.Min
        targetMax = target.Max
        
        if sourceMin==sourceMax:
            remappedVal = (targetMin + targetMax)*0.5
        else:
            remappedVal = targetMin + (targetMax - targetMin) * ((value - sourceMin) / (sourceMax - sourceMin))
        
        if clip == True:
            if val < sourceMin:
                return targetMin
            else:
                if val>sourceMax:
                    return targetMax
                else:
                    return remappedVal
        else:
            return remappedVal
            
        ## proposed usage
        ## oRemappedVal = RemapValue(iVal, iSourceI, iTargetI, iClipped)

elif mode == 1:
    def RemapValue(val, source, target, clip):
        # val is float, source and target Intervals, clip boolean
        value = val 
        sourceMin = source.Max
        sourceMax = source.Min
        targetMin = target.Min
        targetMax = target.Max
        
        if sourceMin==sourceMax:
            remappedVal = (targetMin + targetMax)*0.5
        else:
            remappedVal = targetMin + (targetMax - targetMin) * ((value - sourceMin) / (sourceMax - sourceMin))
        
        if clip == True:
            if val < sourceMin:
                return targetMin
            else:
                if val>sourceMax:
                    return targetMax
                else:
                    return remappedVal
        else:
            return remappedVal
            
        ## proposed usage
        ## oRemappedVal = RemapValue(iVal, iSourceI, iTargetI, iClipped)


#___Geometry_Creation_Scripts___
def GetMeshSphere(position, radius):
    Sphere = rg.Sphere(position,radius)
    SphereBrep = rg.Brep.CreateFromSphere(Sphere)
    #Sphere.ToNurbsSurface()
    
    #Droplet = rg.Mesh.CreateFromSphere(Sphere,4,8)
    #return Droplet
    return SphereBrep

#__Tube_Creation__
"""def BaseCircle(plane,point,radius):
    return rg.Circle(plane,point,radius)"""

def BaseCircle2(plane,radius):
    return rg.ArcCurve(rg.Circle(plane,plane.Origin,radius)) #shortening test

def BaseCircle3(point,vector,radius):
    return rg.ArcCurve(rg.Circle(rg.Plane(point,vector),point,radius)) #different approach

def BaseCircle(plane, radius):
    return rg.ArcCurve(rg.Circle(plane, plane.Origin, radius))
    
def BaseCircle23(point, vector, radius):
    return rg.ArcCurve(rg.Circle(rg.Plane(point,vector), point, radius))
    
    
def getClosedB(stP1, endP1, vector, r1, r2):
    C1= BaseCircle23(stP1, vector, r1)
    C2= BaseCircle23(endP1,vector, r2)
    no_pt=rg.Point3d.Unset
    norm_loft=rg.LoftType.Normal
    breps = rg.Brep.CreateFromLoft([C1,C2],no_pt,no_pt,norm_loft,False)
    m=breps[0]
    return m.CapPlanarHoles(0.01)



#def GetMeshTube(stPt,endPt,stPl,endPl,direction,r1,r2):
def GetMeshTube(stPl,endPl,direction,r1,r2):
    
    CircA = BaseCircle3(stPl,direction,r1)
    CircB = BaseCircle3(endPl,direction,r2)
    
    CircA.ToNurbsCurve()
    CircB.ToNurbsCurve()
    
    crvList = []
    crvList.append(CircA)
    crvList.append(CircB)
    
    caps = rg.Brep.CreatePlanarBreps(crvList)
    
    no_pt=rg.Point3d.Unset
    norm_loft=rg.LoftType.Normal
    breps = rg.Brep.CreateFromLoft([CircA,CircB],no_pt,no_pt,norm_loft,False)
    
    meshOut = breps[0]
    #meshOut.CapPlanarHoles(tol)
    #meshOut.AddSurface(caps[0].)
    #meshOut.AddSurface(caps[1][0])
    #meshOut = rg.Mesh.CreateFromSurface(breps[0])
    #meshOut = rg.Mesh.CreateFromBrep(breps[0])
    #rg.Mesh.CreateFromBrep(breps[0])
    
    return meshOut

def GetDistance(point,root):
    return point.DistanceTo(root)

#__Main
brchInfo = GetBranchInfo(brchList,startingPoint)
#print brchInfo[3][1]

#__Output
#____optional
oStPt = stPtList
oEndPt = endPtList
oVec = vecList
oStPl = stPlList
oEndPl = endPlList
oDistL1 = distList1
oDistL2 = distList2

#___important
oGeometry = outGeo
#oGeometry = GetBranchGeometry(brchInfo)
oGeometry2 = newGeo