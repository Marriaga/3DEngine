"""
Created on Sun Aug 23 22:25:49 2015

@author: Miguel
"""
from __future__ import division
import numpy as np
import FastFunctions as FF
import FastEngine as FE

class Light:
    def __init__(self,PO,VD,Int=0.1):
        self.Orig=PO
        self.n=VD.n
        self.Int=Int

class Camera:
    def __init__(self,SH=20,SV=15,zmin=-10,zmax=10):
        dh=int(SH/2)
        dv=int(SV/2)
        self.xmin=-dh
        self.xmax=dh
        self.ymin=-dv
        self.ymax=dv
        self.zmin=zmin
        self.zmax=zmax
    
    def PointInVision(self,P):
        if P.x>=self.xmin and P.x<=self.xmax and \
        P.y>=self.ymin and P.y<=self.ymax and \
        P.z>=self.zmin and P.z<=self.zmax:
            return True
        else:
            return False


class Point:
    def __init__(self,x,y,z,c=-1):
        self.x=x
        self.y=y
        self.z=z
        if c<0:
           c=FF.randICOL()
        if type(c)==type(tuple()):
           r,g,b=c
           c=FF.getICOL(r,g,b)
        self.c=c
        
    def InView(self,Cam):
        return Cam.PointInVision(self)

    def ApplyTransf(self,Trsf):
        xt,yt,zt,o=np.dot(Trsf.Mat,np.array((self.x,self.y,self.z,1)))
        return Point(xt,yt,zt,c=self.c)

class Vec:
    def __init__(self,PI,PF=None):
        if not PF:
            PF=PI
            PI=Point(0,0,0)
            
        self.x=PF.x-PI.x
        self.y=PF.y-PI.y
        self.z=PF.z-PI.z
        self.n=self.getn()

    def getn(self):        
        n=np.array((self.x,self.y,self.z))
        return n/np.sqrt(np.dot(n,n))
        
class BariConsts():
    def __init__(self,Ps):
        p1,p2,p3=Ps
        self.A01 = p1.y - p2.y
        self.B01 = p2.x - p1.x
        
        self.A12 = p2.y - p3.y
        self.B12 = p3.x - p2.x
        
        self.A20 = p3.y - p1.y
        self.B20 = p1.x - p3.x   
        
class Triangle:
    def __init__(self,P1,P2,P3,Surf=None):
        self.Ps=P1,P2,P3
        self.Surf=Surf
        self.BCts=BariConsts(self.Ps)
        self.Area=self.getArea()
        self.n=self.getn()
        self.lum=0.1
    
    def MouseAlter(self,Mse):
        p1,p2,p3=self.Ps
        p1.x+=Mse.Lx*Mse.speed
        p2.x+=Mse.Lx*Mse.speed
        p3.x+=Mse.Lx*Mse.speed
        p1.y+=Mse.Ly*Mse.speed
        p2.y+=Mse.Ly*Mse.speed
        p3.y+=Mse.Ly*Mse.speed
        self.Update()
    
    def Update(self):
        self.BCts=BariConsts(self.Ps)
        self.Area=self.getArea()

    def getn(self):
        p1,p2,p3=self.Ps
        V=Vec(p1,p2)
        W=Vec(p1,p3)
        nx=V.y*W.z-V.z*W.y
        ny=V.z*W.x-V.x*W.z
        nz=V.x*W.y-V.y*W.x
        return Vec(Point(-nx,-ny,-nz)).n

    def AddLightLum(self,light):
        lum=max(0,-np.dot(light.n,self.n))*light.Int
        self.lum=max(min(self.lum+lum,1),0)
        
    def getArea(self):
        Area=0.5*(self.BCts.B01*self.BCts.A20-self.BCts.B20*self.BCts.A01)
        if not Area==0:
            self.BCts.A01=self.BCts.A01/(2*Area)
            self.BCts.B01=self.BCts.B01/(2*Area)
            self.BCts.A12=self.BCts.A12/(2*Area)
            self.BCts.B12=self.BCts.B12/(2*Area)
            self.BCts.A20=self.BCts.A20/(2*Area)
            self.BCts.B20=self.BCts.B20/(2*Area)
        return Area
 
    def InView(self,Cam):
    #TODO: Make this less rudimentary
        if self.Area<=0:
            return False
        for p in self.Ps:
            if p.InView(Cam):
                return True
        return False 
        
    def draw(self,Cam,Res,Zmap,myarray):
        FE.DrawTriangle(self, Cam, Res, Zmap, myarray)
            
    def getBari(self,px,py):
        p1,p2,p3=self.Ps
        a =  self.BCts.A12*(px - p3.x) + self.BCts.B12*(py - p3.y)
        b =  self.BCts.A20*(px - p3.x) + self.BCts.B20*(py - p3.y)
        c = 1.0 - a - b
        return a,b,c       
        
    def ApplyTransf(self,Trsf):
        p1,p2,p3=tuple(p.ApplyTransf(Trsf) for p in self.Ps)
        return Triangle(p1,p2,p3,self.Surf)
       
class Tetra:
    def __init__(self,P1,P2,P3,P4,Surf=None):
        self.Ps=(P1,P2,P3,P4)        
        self.Surf=Surf
        if not Surf:
            S1=Surf
            S2=Surf
            S3=Surf
            S4=Surf
        else:
            S1=Surf[0]
            S2=Surf[1]
            S3=Surf[2]
            S4=Surf[3]

        T1=Triangle(P1,P2,P4,S1)
        T2=Triangle(P2,P3,P4,S2)
        T3=Triangle(P3,P1,P4,S3)
        T4=Triangle(P1,P3,P2,S4)
        self.Ts=(T1,T2,T3,T4)
        
    def ApplyTransf(self,Trsf):
        P1,P2,P3,P4=tuple(t.ApplyTransf(Trsf) for t in self.Ps)
        return Tetra(P1,P2,P3,P4,self.Surf)
    
    def AddLightLum(self,light):
        for t in self.Ts:
            t.AddLightLum(light)
            
    def InView(self,Cam):
    #TODO: Make this less rudimentary
        for t in self.Ts:
            if t.InView(Cam):
                return True
        return False
    
    def draw(self,Cam,Res,Zmap,myarray):
        for t in self.Ts:
            if t.InView(Cam):
                t.draw(Cam,Res,Zmap,myarray)







