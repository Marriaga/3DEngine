

from __future__ import division
import Shapes as Sh


def addli(x,i,v):
    if len(x)-1<i:
        k=i-len(x)+1
        t=[0 for j in range(k)]
        x.extend(t)
    x[i]=v

def listtopoints(points):
    Pts=[]
    for cs in points:
        try:
            x,y,z = cs
            Pts.append(Sh.Point(x,y,z))
        except:
            Pts.append([])
    return Pts

def listtotriangles(Pts,triangles,Surf=None):
    Ts=[]
    for ps in triangles:
        try:
            ip1,ip2,ip3 = ps
            p1=Pts[ip1]
            p2=Pts[ip2]
            p3=Pts[ip3]
            Ts.append(Sh.Triangle(p1,p2,p3,Surf))
        except:
            print 'ERROR: Invalid point for triangle definition'
    return Ts

def readfile(filename):
    f=open(filename,'r')
    #f=open('testmesh','r')
    #f=open('boltmesh','r')

    datatype=0 #1-Parameters,2-Points,3-Triangles
    params=dict()
    points=[]
    triangles=[]
    for line in f:
        line=line.strip()
        if line=='Parameters':
            datatype=1
        elif line=='Points':
            datatype=2
        elif line=='Triangles':
            datatype=3
        elif line=='':
            next
        else:
            if datatype==1:
                x=line.split('=')
                params[x[0]]=float(x[1])
                pkeys=params.keys()
            elif datatype==2:
                i,x,y,z = [k.strip() for k in line.split(',')]
                i=int(i)
                coords=[x,y,z]
                for ic,c in enumerate(coords):
                    sign=1
                    if c[0]=='-':
                        c=c[1:]
                        sign=-1
                    try:
                        c=float(c)
                    except:
                        if c in pkeys:
                            c=params[c]
                        else:
                            print 'ERROR: No such parameter: ' + c
                    coords[ic]=c*sign
                addli(points,i,coords)
            elif datatype==3:
                i,x,y,z = [k.strip() for k in line.split(',')]
                try:
                    i=int(i)
                    ps=[int(x),int(y),int(z)]
                except:
                    print 'ERROR: Incorrect Triangle: ' + str(i)
                addli(triangles,i,ps)

    f.close()

    return points,triangles

def getmesh(filename,Surf=None):
    points,triangles=readfile(filename)
    Pts=listtopoints(points)
    Ts=listtotriangles(Pts,triangles,Surf)
    for i in range(Pts.count([])):
        Pts.remove([])
    return Pts,Ts
    
