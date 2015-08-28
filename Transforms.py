"""
@author: Miguel
"""
from __future__ import division
import numpy as np

class Rotation:
    def __init__(self,ang,dim):
        self.ang=ang
        self.dim=dim
        self.Mat=self.getMat()
        
    def getMat(self):
        dim=self.dim
        ang=self.ang
        s=np.sin(ang*np.pi/180)
        c=np.cos(ang*np.pi/180)
        Mat=np.eye(4)
        if dim==1:
            Mat[1,1]=c
            Mat[1,2]=-s
            Mat[2,1]=s
            Mat[2,2]=c
        elif dim==2:
            Mat[0,0]=c
            Mat[0,2]=-s
            Mat[2,0]=s
            Mat[2,2]=c
        elif dim==3:
            Mat[0,0]=c
            Mat[0,1]=-s
            Mat[1,0]=s
            Mat[1,1]=c
        else:
            print 'ERROR: dim in [1,2,3]'
        return Mat
        
    def Modify(self,ang=None,dim=None):
        if not ang==None:
            self.ang=ang
        if not dim==None:
            self.dim=dim
        self.Mat=self.getMat()

class Scaling:
    def __init__(self,s,dim):
        self.s=s
        self.dim=dim
        self.Mat=self.getMat()
        
    def getMat(self):
        dim=self.dim
        s=self.s
        Mat=np.eye(4)
        if dim==1:
            Mat[0,0]=s
        elif dim==2:
            Mat[1,1]=s
        elif dim==3:
            Mat[2,2]=s
        else:
            print 'ERROR: dim in [1,2,3]'
        return Mat
        
    def Modify(self,s=None,dim=None):
        if not s==None:
            self.s=s
        if not dim==None:
            self.dim=dim
        self.Mat=self.getMat()

class Translation:
    def __init__(self,t,dim):
        self.t=t
        self.dim=dim
        self.Mat=self.getMat()
        
    def getMat(self):
        dim=self.dim
        t=self.t
        Mat=np.eye(4)
        if dim==1:
            Mat[0,3]=t
        elif dim==2:
            Mat[1,3]=t
        elif dim==3:
            Mat[2,3]=t
        else:
            print 'ERROR: dim in [1,2,3]'
        return Mat
        
    def Modify(self,t=None,dim=None):
        if not t==None:
            self.t=t
        if not dim==None:
            self.dim=dim
        self.Mat=self.getMat()          
        
class Transform:
    def __init__(self):
        self.TransformList=[]
        self.Mat=np.eye(4)
    
    def AddTransf(self,TObj):
        self.TransformList.append(TObj)
        self.Mat=np.dot(TObj.Mat,self.Mat)

    def UpdateMat(self):
        TL=self.TransformList
        Mat=np.eye(4)
        for TObj in TL:
            Mat=np.dot(TObj.Mat,Mat)
        self.Mat=Mat




