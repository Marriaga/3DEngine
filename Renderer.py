"""
@author: Miguel
"""
from __future__ import division
import numpy as np

class Renderer:
    def __init__(self,Cam,Res):
        self.Cam=Cam
        self.Res=Res
        self.Objects=[]
        self.ObjectsT=[]
        self.Transforms=[]
        self.Lights=[]

        myarray = np.zeros(Res, dtype=np.int32)
        myarray[:,:] = 256**3-1
        Zmap = np.zeros(Res, dtype=np.double)
        Zmap[:,:] = Cam.zmax

        self.myarray=myarray
        self.Zmap=Zmap

    def AddObject(self,obj):
        self.Objects.append(obj)
        self.ObjectsT.append(obj)
        
    def AddTransf(self,Trsf):
        self.Transforms.append(Trsf)
        
    def AddLightLum(self,light):
        self.Lights.append(light)
            
    def ApplyTransf(self):
        self.ObjectsT=self.Objects
        for Trsf in self.Transforms:
            self.ObjectsT=[obj.ApplyTransf(Trsf) for obj in self.ObjectsT]
            
    def ApplyLight(self):
        for light in self.Lights:
            for obj in self.ObjectsT:
                obj.AddLightLum(light)        
        
    def Render(self):
        self.myarray[:,:] = 256**3-1
        self.Zmap[:,:]=self.Cam.zmax
        
        for obj in self.ObjectsT:
            if obj.InView(self.Cam):
                obj.draw(self.Cam,self.Res, self.Zmap,self.myarray)

    def MouseTransform(self,Mse):
        
        da1=-Mse.Ry*Mse.speed[0]
        da2=-Mse.Rx*Mse.speed[0]
        dd1=Mse.Lx*Mse.speed[1]
        dd2=Mse.Ly*Mse.speed[1]

        Transform=self.Transforms[0]        #Get first Transformation Set (TS)

        Atranfs=Transform.TransformList[0]  #Get first transformation (rotation)
        Atranfs.Modify(ang=Atranfs.ang+da1) #Change the angle of rotation
        Atranfs=Transform.TransformList[1]  #Get second transformation (rotation)
        Atranfs.Modify(ang=Atranfs.ang+da2) #Change the angle of rotation

        Atranfs=Transform.TransformList[2]  #Get third transformation (translation)
        Atranfs.Modify(t=Atranfs.t+dd1) #Change the translation
        Atranfs=Transform.TransformList[3]  #Get third transformation (translation)
        Atranfs.Modify(t=Atranfs.t+dd2) #Change the translation

        Transform.UpdateMat()               #Update the Matrix of the TS
    
        self.ApplyTransf()    #Apply the transformations
        self.ApplyLight()     #Apply the lighting
        self.Render() #Render the image
        
        return self.myarray


