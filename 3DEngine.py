#!/usr/bin/python
from __future__ import division
import numpy as np
#import scipy as sp
from Tkinter import *
from PIL import Image, ImageTk
import math
import colorsys

#----------------------------------------------------------------------

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

#----------------------------------------------------------------------

class Point:
    def __init__(self,x,y,z,c=None):
        self.x=x
        self.y=y
        self.z=z
        if not c:
            gg1=np.random.randint(0,256)
            gg2=np.random.randint(0,256)
            gg3=np.random.randint(0,256)
            c=(gg1,gg2,gg3)
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

class Triangle:
    def __init__(self,P1,P2,P3,Surf=None):
        self.Ps=P1,P2,P3
        self.Surf=Surf
        self.Area=self.getArea()
        self.n=self.getn()
        self.lum=0.1

    def getArea(self):
        p1,p2,p3=self.Ps
        return 0.5*((p2.x-p1.x)*(p3.y-p1.y)-(p3.x-p1.x)*(p2.y-p1.y))
        
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
        
    def InView(self,Cam):
    #TODO: Make this less rudimentary
        if self.Area<=0:
            return False
        for p in self.Ps:
            if p.InView(Cam):
                return True
        return False
        
    def getBari(self,px,py):
        p1,p2,p3=self.Ps
        den=(p2.y - p3.y)*(p1.x - p3.x) + (p3.x - p2.x)*(p1.y - p3.y)
        if den==0.0:
            return (0,0,0),False
        a = ((p2.y - p3.y)*(px - p3.x) + (p3.x - p2.x)*(py - p3.y)) /den
        b =  ((p3.y - p1.y)*(px - p3.x) + (p1.x - p3.x)*(py - p3.y)) /den 
        c = 1.0 - a - b
        if a>=0 and a<=1 and b>=0 and b<=1 and c>=0 and c<=1:
            isin= True
        else:
            isin= False
        return (a,b,c),isin        
        
    def getz(self,Bari):
        p1,p2,p3=self.Ps
        a,b,c=Bari
        return a*p1.z+b*p2.z+c*p3.z
    
    def getcol(self,Bari):
        p1,p2,p3=self.Ps
        a,b,c=Bari
        colnode = tuple(int(a*co1+b*co2+c*co3) for co1,co2,co3 in zip(p1.c,p2.c,p3.c))
        r, g, b = [x/255.0 for x in colnode]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l=self.lum
        return tuple(int(x*255.0) for x in colorsys.hls_to_rgb(h, l, s))             
                    
        
    def draw(self,Cam,Res):
        p1,p2,p3=self.Ps
        #Resolution
        Nx,Ny=Res
        
        #size/pixel
        dx=(Cam.xmax-Cam.xmin)/Nx
        dy=(Cam.ymax-Cam.ymin)/Ny
        
        #Extremes of triangle 2D coords.
        minX=min(p1.x,p2.x,p3.x)
        maxX=max(p1.x,p2.x,p3.x)
        minY=min(p1.y,p2.y,p3.y)
        maxY=max(p1.y,p2.y,p3.y)
        
        #Rectangle that contains the points and is inside Cam
        Nxmin=max(0,int(math.floor((minX-Cam.xmin)/dx)))
        Nxmax=min(Nx-1,int(math.floor((maxX-Cam.xmin)/dx)))
        Nymint=max(0,int(math.floor((minY-Cam.ymin)/dy)))
        Nymaxt=min(Ny-1,int(math.floor((maxY-Cam.ymin)/dy)))
        Nymin=Ny-1-Nymaxt     
        Nymax=Ny-1-Nymint        
        
        
        pixs=[]
        for ix in range(Nxmin,Nxmax+1):
            for iy in range(Nymin,Nymax-1):
                XX=Cam.xmin+dx/2+ix*dx
                YY=Cam.ymin+dy/2+(Ny-1-iy)*dy
                Bari,isin=self.getBari(XX,YY)
                if isin:
                    z=self.getz(Bari)
                    col=self.getcol(Bari)
                    pixs.append((ix,iy,z,col))                
        return pixs

    def ApplyTransf(self,Trsf):
        p1,p2,p3=tuple(p.ApplyTransf(Trsf) for p in self.Ps)
        return Triangle(p1,p2,p3,self.Surf)
        
class Tetra:
    def __init__(self,P1,P2,P3,P4,Surf=None):
        self.Ps=(P1,P2,P3,P4)
        T1=Triangle(P1,P2,P4,Surf)
        T2=Triangle(P2,P3,P4,Surf)
        T3=Triangle(P3,P1,P4,Surf)
        T4=Triangle(P1,P3,P2,Surf)
        self.Ts=(T1,T2,T3,T4)
        self.Surf=Surf
        
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
    
    def draw(self,Cam,Res):
        pixs=[]
        for t in self.Ts:
            if t.InView(Cam):
                pixs.extend(t.draw(Cam,Res))
        return pixs

#----------------------------------------------------------------------

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

#----------------------------------------------------------------------
        
class Renderer:
    def __init__(self,Cam,Res=(800,600)):
        if Cam==[]:
            print("ERROR: Cam cannont be empty in Renderer")
        self.Cam=Cam
        self.Res=Res
        self.Objects=[]
        self.ObjectsT=[]
        self.Transforms=[]
        self.Lights=[]
        self.Img=Image.new('RGB', Res,"white") # create a new blank image
    
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
        self.Img=Image.new('RGB', self.Res,"white")
        pixels = self.Img.load() # create the pixel map
        Zmap=np.zeros(self.Img.size)
        Zmap[:,:]=self.Cam.zmax        
        
        for obj in self.ObjectsT:
            if obj.InView(self.Cam):
                pixs=obj.draw(self.Cam,self.Res)
                for ix,iy,z,col in pixs:
                    if Zmap[ix,iy]>=z:
                        Zmap[ix,iy]=z
                        pixels[ix,iy]=col
        #self.Img.show()  #Old viewing


#----------------------------------------------------------------------

class MainWindow():
    def __init__(self, Root,Rend):
        
        #Store the Renderer
        self.Rend=Rend    
        #width,height=self.Rend.Res
        width,height=800,600
        self.wh=(width,height)
        
        #Store the Tk Object
        self.Root=Root
        self.Root.geometry(str(width)+'x'+str(height+40))
        
        #Set the Active flag as False, i.e. the animation is off
        self.active=False

        # Canvas for image
        self.canvas = Canvas(Root, width=width, height=height)
        self.canvas.grid(row=1, column=0)

        # Image initialization (it is initally blank)
        self.image = ImageTk.PhotoImage(Rend.Img.resize((width,height)))

        # Set Image on Canvas
        self.image_on_canvas = self.canvas.create_image(width/2, height/2, image = self.image)

        # Button to start/stop animation
        self.button = Button(Root, text="Start", command=self.onButton)
        self.button.grid(row=0, column=0)

    #----------------

    def onButton(self):
        if not self.active:
            self.button.configure(text="Stop")
            self.active=True
            self.RedoPic()
        elif self.active:
            self.button.configure(text="Continue")
            self.active=False
        
    def RedoPic(self):
        Transform=self.Rend.Transforms[0]  #Get first Transformation Set (TS)
        Atranfs=Transform.TransformList[0] #Get first transformation (rotation)
        Atranfs.Modify(ang=Atranfs.ang+10) #Change the angle of rotation
        Atranfs=Transform.TransformList[1] #Get second transformation (rotation)
        Atranfs.Modify(ang=Atranfs.ang+5)  #Change the angle of rotation
        Transform.UpdateMat()              #Update the Matrix of the TS
        
        self.Rend.ApplyTransf() #Apply the transformations
        self.Rend.ApplyLight()  #Apply the lighting
        self.Rend.Render()      #Render the image
        
        #Resize, Save and put image on canvas
        self.image = ImageTk.PhotoImage(self.Rend.Img.resize(self.wh))
        self.canvas.itemconfig(self.image_on_canvas, image = self.image)
        
        #Keep changing the angle until process is stopped
        if self.active:
            self.Root.after(4, self.RedoPic)

#----------------------------------------------------------------------
#----------------------------------------------------------------------

## SET-UP

#Create 4 points: Point(x,y,z,(R,G,B))
p1=Point(-2,-2, 4,(0,255,255))
p2=Point( 4, 0.1, 4,(255,255,0))
p3=Point( 0.1, 4, 4,(255,0,0))
p4=Point( -0.1, -0.1, 0,(100,100,100))
#Create a Tetrahedron 
TH1=Tetra(p1,p2,p3,p4)

#Create a Transformation Set
TS1=Transform()
#Add several transformations to the set
TS1.AddTransf(Rotation(130,3))
TS1.AddTransf(Translation(2,2))
TS1.AddTransf(Translation(1,3))
TS1.AddTransf(Translation(1,1))
#Create a new Tetrahedron by applying the
#transformation set to the first tetrahedron
TH2=TH1.ApplyTransf(TS1)

#Create Camera (very basic for now)
cam=Camera()

#Create a new transformation set and
#add Rotation tranformations to the set
#(These will be the transformations changed 
# in the GUI to make the objects rotate)
TS2=Transform()
TS2.AddTransf(Rotation(0,3))
TS2.AddTransf(Rotation(0,2))

#Create First Light Source
L1O=Point(5,0,2) #Point of origin (not used for now)
L1D=Vec(Point(-1,0,0)) #Direction
L1=Light(L1O,L1D,0.5) #Create Light object

#Create Second Light Source
L2O=Point(0,-3,0)
L2D=Vec(Point(0,1,2))
L2=Light(L2O,L2D,0.3)

#Create Renderer Object: Renderer(Camera,Resolution)
rend=Renderer(cam,Res=(400,300))
#Add the Tetrahedra to the Renderer
rend.AddObject(TH1)
rend.AddObject(TH2)
#Add the transformation (rotaiton)
rend.AddTransf(TS2)
#Add the lights
rend.AddLightLum(L1)
rend.AddLightLum(L2)

#----------------------------------------------------------------------

#Tkinter

root = Tk()
#root = Toplevel()
MainWindow(root,rend)
root.mainloop()




