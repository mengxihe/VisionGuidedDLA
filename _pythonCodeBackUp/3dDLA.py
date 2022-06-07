__author__ = "Mengxi He"

import Rhino.Geometry as rg
import Grasshopper.Kernel as gk
import Grasshopper.Kernel.Types as gkt
import random as rd
import math
import rhinoscriptsyntax as rs
import perlin as p

sn=p.SimplexNoise()
boundarySize = 200


class Util:
    def __init__(self):
        pass

    @staticmethod
    def RandomUnitVector():
        # generate a random UnitVector
        # self.lock.acquire()
        theta = 2.0 * math.pi * rd.random()
        phi = math.acos(2.0 * rd.random() - 1.0)
        return rg.Vector3d(math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), math.cos(phi))
        # self.lock.release()

    @staticmethod
    def RandomUnitVectorUpperHemisphere():
        # self.lock.acquire()
        theta = 2.0 * math.pi * rd.random()
        phi = math.acos(2.0 * rd.random() - 1.0)
        return rg.Vector3d(math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta), abs(math.cos(phi)))
        # self.lock.release()


class FreeParticle:
    def __init__(self, environmentBoundary, particleRadius):
        self.Position = rg.Point3d.Origin + Util.RandomUnitVectorUpperHemisphere() * environmentBoundary
        self.Velocity = Util.RandomUnitVector() * particleRadius


class DlaSystem:
    def __init__(self, initialParticles, freeParticlesCount):
        self.FreeparticlesCount = freeParticlesCount
        self.Particles = initialParticles
        self.ff=FlowField(boundarySize,10,scalePerlin)
        self.Branches = []
        self.clusterReach = 0.0
        self.particleRadius = 5.0
        self.environmentBoundary = 0.0
        for p in self.Particles:
            d = p.DistanceTo(rg.Point3d.Origin)
            if d > self.clusterReach:
                self.clusterReach = d
        self.UpdateEnvironmentBoundary()
        self.FreeParticles = []
        self.fParticle = FreeParticle(self.environmentBoundary, self.particleRadius)
        for i in range(self.FreeparticlesCount):
            self.FreeParticles.append(self.fParticle)
        self.rTree=rg.RTree()
        for i in range (len(self.Particles)):
            self.rTree.Insert(self.Particles[i],i)

    def UpdateEnvironmentBoundary(self):
        self.environmentBoundary = self.clusterReach * 1.0
        if self.environmentBoundary < self.particleRadius * 1.0:
            self.environmentBoundary = self.particleRadius * 1.0

        
    def Iterate(self):
        for i in range(len(self.FreeParticles)):
            freeParticle = self.FreeParticles[i]
            # apply random force to the particle
            v= self.ff.lookUp(freeParticle.Velocity)
            randomForce = Util.RandomUnitVector() * self.particleRadius + v/10  +iExternalVevtor
            freeParticle.Velocity += randomForce

            if freeParticle.Velocity.Length > self.particleRadius:
                freeParticle.Velocity *= self.particleRadius / freeParticle.Velocity.Length
            freeParticle.Position += freeParticle.Velocity#+iExternalVevtor
            self.ProcessBoundary(freeParticle)
            # if the particle wanders out of range, respawn it
            if freeParticle.Position.DistanceTo(rg.Point3d.Origin) > self.environmentBoundary and freeParticle.Position.Z < 0.0:
                self.FreeParticles[i] = FreeParticle(self.environmentBoundary, self.particleRadius)
                continue

            # Otherwise check if the free Particle collide with the cluster
            collidedParticle = rg.Point3d.Unset
            for particle in self.Particles:
                if freeParticle.Position.DistanceTo(particle) <2.0 * self.particleRadius:
                    collidedParticle = particle

            def SearchCallback(sender, args):
                collidedParticle=self.Particles[args.Id]
                args.Cancel=True
            self.rTree.Search(rg.Sphere(freeParticle.Position, 2.0*self.particleRadius), SearchCallback)

            # if a collision has been found
            if collidedParticle.IsValid:
                self.Particles.append(freeParticle.Position)
                #self.Branches.append(rg.Line(freeParticle.Position, collidedParticle))
                self.Branches.append(rg.Line(collidedParticle,freeParticle.Position))
                self.FreeParticles[i] = FreeParticle(self.environmentBoundary, self.particleRadius)
                distanceToOrigin = freeParticle.Position.DistanceTo(rg.Point3d.Origin)
                if self.clusterReach < distanceToOrigin:
                    self.clusterReach = distanceToOrigin

    def ProcessBoundary(self, particle):
        if particle.Position.X<0:
            particle.Position.X=boundarySize
        elif particle.Position.X>boundarySize:
            particle.Position.X=0
        
        if particle.Position.Y<0:
            particle.Position.Y=boundarySize
        elif particle.Position.Y>boundarySize:
            particle.Position.Y=0

        if particle.Position.Z<0:
            particle.Position.Z=boundarySize
        elif particle.Position.Z>boundarySize:
            particle.Position.Z=0
        
        self.UpdateEnvironmentBoundary()


class FlowField:
    def __init__(self, size, res, scalePerlin):
        self.size=size
        self.scaleP=scalePerlin
        self.res=res
        self.pointsPerSide= int(size/res)
        self.grid=self.createGrid()
    def createGrid(self):
        L=[]
        for i in range(self.pointsPerSide):
            L.append([])
            for j in range(self.pointsPerSide):
                L[i].append([])
                for k in range(self.pointsPerSide):
                    L[i][j].append([])
                    point=[i*self.res, j*self.res, k*self.res]
                    perVal= sn.noise3(i*self.scaleP, j*self.scaleP, k*self.scaleP)
                    xVec=[self.res,0,0]
                    rotV=rs.VectorRotate(xVec, 360*perVal, [0,0,1])
                    endV=rs.VectorCreate(point,rotV)
                    L[i][j][k]=rotV
        return L
    def lookUp(self, vec):
        x=int(vec[0]/self.res)
        y=int(vec[1]/self.res)
        z=int(vec[2]/self.res)
        return self.grid[x][y][z]
        
    def drawFirstLayer(self):
        
        layer=[]
        for i in range(self.pointsPerSide):
            for j in range(self.pointsPerSide):
                point=[i*self.res, j*self.res, 0]
                endV=rs.VectorCreate(point,self.lookUp(point))
                layer.append(rs.AddLine(point, endV))
        return layer

# main program

if iReset or "myDlaSystem" not in globals():
    InitialParticles = iInitialParticles
    InitialBranches = []
    FreeParticlesCount = iFreeParticlesCount
    myDlaSystem = DlaSystem(InitialParticles, FreeParticlesCount)


else:
    for i in range(iSubiterations):
        myDlaSystem.Iterate()




Particles = []
for particle in myDlaSystem.Particles:
    Particles.append(gkt.GH_Point(particle))

Branches = []
for line in myDlaSystem.Branches:
    Branches.append(gkt.GH_Line(line))

FreeParticles = []
for freeParticle in myDlaSystem.FreeParticles:
    FreeParticles.append(gkt.GH_Point(freeParticle.Position))
