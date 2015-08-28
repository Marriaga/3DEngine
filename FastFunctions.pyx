# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 22:25:49 2015

@author: Miguel
"""
from __future__ import division
import numpy as np
cimport numpy as np
#cimport cython

#DTYPE = np.int32
#ctypedef np.int32_t DTYPE_t

# COLOR MANIPULATION
def randICOL():
    cdef int R,G,B
    cdef int I
    R=int(np.random.rand()*255)
    G=int(np.random.rand()*255)
    B=int(np.random.rand()*255)
    return getICOL(R,G,B)
    

def getRGB(int icol):
    cdef int R,G,B
    R=icol>>16
    G=(icol>>8)%256
    B=icol%256
    return R,G,B

def getICOL(int R, int G, int B):
    return R<<16|G<<8|B

def getLum(int icol):
    cdef int R,G,B
    R,G,B = getRGB(icol)
    return (min(R,G,B)+max(R,G,B))/(2*255)

def setLum(int icol,double NLum):
    cdef int R,G,B
    cdef int m,M
    cdef double OLum
    cdef double alpha
    R,G,B = getRGB(icol)
    M=max(R,G,B)
    m=min(R,G,B)
    OLum=(M+m)/(2*255)
    if OLum==0:
        OLum=1/255
        R,G,B=1,1,1
        M=1
        m=1
    alpha=NLum/OLum
    if M*alpha>255:
        if m==0:
            m=1
            if R==0: R=1
            if G==0: G=1
            if B==0: B=1
        alpha=255*(2*NLum-1)/m
    R=min(int(R*alpha),255)
    G=min(int(G*alpha),255)
    B=min(int(B*alpha),255)
    return getICOL(R,G,B)

def getcol(int c1, int c2, int c3, double a, double b, double c,double lum):
     cdef int r1,g1,b1
     cdef int r2,g2,b2
     cdef int r3,g3,b3
     cdef int R,G,B
     cdef int icol
     r1,g1,b1=getRGB(c1)
     r2,g2,b2=getRGB(c2)
     r3,g3,b3=getRGB(c3)
     R=int(a*r1+b*r2+c*r3)
     G=int(a*g1+b*g2+c*g3)
     B=int(a*b1+b*b2+c*b3)
     icol=getICOL(R,G,B)
     icol=setLum(icol,lum)
     return icol
