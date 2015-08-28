# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 21:52:11 2015

@author: Miguel
"""
from __future__ import division
import pygame, random, time
import numpy as np
import pyximport
pyximport.install(setup_args={'include_dirs': np.get_include()})
import FastEngine as FE
import FastFunctions as FF
import Shapes as Sh
import Transforms as Tf
import Renderer as Rd


class MouseMove():
    def __init__(self,speed=[1.0,0.2]):
        self.Lx=0.0
        self.Ly=0.0
        self.Rx=0.0
        self.Ry=0.0
        self.speed=speed

    def ChangeSpeed(self,val,dim=None):
        if not dim:
            dim=[0,1]
        elif type(dim)!=type(list()):
            dim=[dim]
        for i in dim:
            self.speed[i]=self.speed[i]*val

    def clear(self):
        self.Lx=0.0
        self.Ly=0.0
        self.Rx=0.0
        self.Ry=0.0

    def Print(self):
        print self.Lx,self.Ly,self.Rx,self.Ry


#Set-Up
RESOLUTION=(800,600)
TARGFPS=60

#Create 4 points: Point(x,y,z,(R,G,B))
p1=Sh.Point(-2,-2, 4,(0,255,255))
p2=Sh.Point( 4, 0.1, 4,(255,255,0))
p3=Sh.Point( 0.1, 4, 4,(255,0,0))
p4=Sh.Point( -0.1, -0.1, 0,(100,100,100))
#Create a Tetrahedron 
TH1=Sh.Tetra(p1,p2,p3,p4)
    
#Create a Transformation Set
TS1=Tf.Transform()
#Add several transformations to the set
TS1.AddTransf(Tf.Rotation(130,3))
TS1.AddTransf(Tf.Translation(2,2))
TS1.AddTransf(Tf.Translation(1,3))
TS1.AddTransf(Tf.Translation(1,1))
#Create a new Tetrahedron by applying the
#transformation set to the first tetrahedron
TH2=TH1.ApplyTransf(TS1)
    
#Create Camera (very basic for now)
cam=Sh.Camera()
    
#Create a new transformation set and
#add Rotation tranformations to the set
#(These will be the transformations changed 
# in the GUI to make the objects rotate)
TS2=Tf.Transform()
TS2.AddTransf(Tf.Rotation(0,1))
TS2.AddTransf(Tf.Rotation(0,2))
TS2.AddTransf(Tf.Translation(0,1))
TS2.AddTransf(Tf.Translation(0,2))

#Create First Light Source
L1O=Sh.Point(5,0,2) #Point of origin (not used for now)
L1D=Sh.Vec(Sh.Point(-1,0,0)) #Direction
L1=Sh.Light(L1O,L1D,0.5) #Create Light object

#Create Second Light Source
L2O=Sh.Point(0,-3,0)
L2D=Sh.Vec(Sh.Point(0,1,2))
L2=Sh.Light(L2O,L2D,0.3)
    
#Create Renderer Object: Renderer(Camera,Resolution)
rend=Rd.Renderer(cam,RESOLUTION)
#Add the Tetrahedra to the Renderer
rend.AddObject(TH1)
rend.AddObject(TH2)
#Add the transformation (rotaiton)
rend.AddTransf(TS2)
#Add the lights
rend.AddLightLum(L1)
rend.AddLightLum(L2)
    
#    rend.ApplyTransf() #Apply the transformations
#    rend.ApplyLight()  #Apply the lighting
#    myarray=rend.Render()      #Render the image



# PYGAME LOOP
pygame.init()
Surface = pygame.display.set_mode(RESOLUTION) # screen width/height
pygame.display.set_caption('New Engine') # screen caption
clock = pygame.time.Clock() # initialize clock.

Mse=MouseMove()

t0=time.time()
nl=0
# Loop until the user clicks close button
runit = True
while runit:
    Mse.clear()
    
    # write event handlers here
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runit=False
        if event.type == pygame.KEYDOWN:
            key=event.unicode
            if key=='q':
                Mse.ChangeSpeed(5/4,0) #speed up angle
            elif key=='a':
                Mse.ChangeSpeed(4/5,0) #slow down angle
            elif key=='z':
                Mse.speed[0]=1.0 #reset angle
            elif key=='w':
                Mse.ChangeSpeed(5/4,1) #speed up translation
            elif key=='s':
                Mse.ChangeSpeed(4/5,1) #slow down translation
            elif key=='x':
                Mse.speed[1]=1.0 #reset translation

        if event.type == pygame.MOUSEMOTION:
            rel = event.rel
            if event.buttons[0]: #LeftButton
                Mse.Lx = rel[0]
                Mse.Ly = -rel[1]
            if event.buttons[2]: #RightButton
                Mse.Rx = rel[0]
                Mse.Ry = -rel[1]
                
    # Update Screen Pixels
    myarray=rend.MouseTransform(Mse)
    pygame.surfarray.blit_array(Surface,myarray)
    pygame.display.update()

    # Set fps
    clock.tick(TARGFPS)

    # Check FPS
    nl+=1     
    if nl==100:
        t1=time.time()
        fps=round(nl/(t1-t0),2)
        print '    Time = ' + str(round(t1-t0,2)) + 's for ' + str(nl) + ' frames'
        print '    FPS  = '+str(fps)
        t0=time.time()
        nl=0
        #runit=False
 
# close the window and quit
pygame.quit()
