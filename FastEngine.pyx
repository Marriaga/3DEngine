# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 22:25:49 2015

@author: Miguel
"""
from __future__ import division
import numpy as np
import math
cimport numpy as np
cimport cython
import cProfile
import FastFunctions as FF

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func




DTYPE = np.int32
ctypedef np.int32_t DTYPE_t

#@do_cprofile
@cython.boundscheck(False) # turn of bounds-checking for entire function
def DrawTriangle(self, Cam, tuple Res, np.ndarray[double, ndim=2] Zmap, np.ndarray[DTYPE_t, ndim=2] myarray):
    cdef int Nx,Ny
    cdef double dx,dy
    cdef double minX,maxX,minY,maxY
    cdef int Nxmin,Nxmax,Nymint,Nymaxt,Nymin,Nymax
    cdef double XX,YY
    cdef double a0,b0,c0
    cdef double a, b, c
    cdef int ix,iy
    cdef int isin
    cdef double z, z1, z2, z3
    cdef DTYPE_t col1,col2,col3
    cdef DTYPE_t icol
    cdef double lum
    cdef double A12dx,A20dx,A01dx
    cdef double B12dy,B20dy,B01dy
    
    p1,p2,p3=self.Ps
    z1=p1.z
    z2=p2.z
    z3=p3.z
    col1=p1.c
    col2=p2.c
    col3=p3.c
    lum=self.lum
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
        
    #Bottom Lower Corner
    XX=Cam.xmin+dx/2+Nxmin*dx
    YY=Cam.ymin+dy/2+(Ny-1-Nymin)*dy
    a0,b0,c0=self.getBari(XX,YY)

    #Bari Constants
    A12dx=self.BCts.A12*dx
    A20dx=self.BCts.A20*dx
    A01dx=self.BCts.A01*dx
    B12dy=self.BCts.B12*dy
    B20dy=self.BCts.B20*dy
    B01dy=self.BCts.B01*dy
    
    for iy in xrange(Nymin,Nymax-1):
        a,b,c=a0,b0,c0
        for ix in xrange(Nxmin,Nxmax+1):
            if a>=0 and b>=0 and c>=0:
                z=a*z1+b*z2+c*z3
                if Zmap[ix,iy]>=z:
                    Zmap[ix,iy]=z
                    icol=FF.getcol(col1,col2,col3,a,b,c,lum)
                    myarray[ix,iy]=icol
            a+=A12dx
            b+=A20dx
            c+=A01dx
        a0-=B12dy
        b0-=B20dy
        c0-=B01dy
            
