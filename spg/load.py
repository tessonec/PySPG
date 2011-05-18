#! /usr/bin/python
# -*- coding: utf-8 -*-

import PyGrace
import sys
from math import *
try:
  import numpy
except:
  import Numeric as numpy

def loadData (s):
  fIn=open(s)

  return  [
            map(float,strLine.replace("D","E").strip().split() )
            for strLine in fIn.readlines() if strLine.find("nan")==-1 and strLine
          ]


def dumpData (s,data):
  try:
    fout=open(s,"w")
  except:

    sys.stderr.write("error!!! opening for write file: %s...\n"%s)
    sys.stderr.write("gently quitting...\n")
    sys.exit()

  for line in data:
    fout.write("\t".join([str(i) for i in line])+"\n")



def loadXY (s,xCol=0,yCol=1):
  """
    if xCol=None, the index is used
  """
  fin=open(s,'r')
  out=[]
  valueX=0.
  for contenido in fin :
    line = contenido.strip().split()
    try:
     if xCol == None:
      out.append([valueX, float(line[yCol]) ])
     else:
      out.append([ float(line[xCol]), float(line[yCol]) ])
    except:
      sys.stderr.write("skip line %7d: >>>%s<<< \n"%(valueX,contenido.strip()))

    valueX+=1.
  return out

def loadMeanXY (s,xCol=0,yCol=1):
  """
    if xCol=None, the index is used
  """
  fin=open(s,'r')
  dic_val={}
  dic_cnt = {}
  for contenido in fin :
   
    line = map(float, contenido.split() )
#    print line
    xval = line[ xCol ]
    yval = line[ yCol ]
    if xval in dic_val.keys():
      dic_val[xval]+=yval
      dic_cnt[xval]+=1.
    else:	
      dic_val[xval]=yval
      dic_cnt[xval]=1.

  return [ [key, dic_val[key]/dic_cnt[key] ] for key in sorted(dic_cnt) ]


def loadXYZ (s,xCol=0,yCol=1,zCol=2):
  """
    if xCol=None, the index is used
  """
  fin=open(s,'r')
  out=[]
  valueX=0.
  for contenido in fin :
    line = contenido.strip().split()
    try:
     if xCol == None:
      out.append([valueX, float(line[yCol]), float(line[zCol]) ])
     else:
      out.append([ float(line[xCol]), float(line[yCol]), float(line[zCol]) ])
    except:
      sys.stderr.write("skip line %7d: >>>%s<<< \n"%(valueX,contenido.strip()))

    valueX+=1.
  return out


def loadY (s,yCol=0):

  fin=open(s,'r')
  out=[]
  valueX=0.
  for contenido in fin :

    try:
      out.append( float(contenido.strip().split()[yCol]) )
    except:
      sys.stderr.write("skip line %7d: >>>%s<<< \n"%(valueX,contenido.strip()))

    valueX+=1.
  return out

def transformXY(ls,xFormula="$x",yFormula="$y"):
  xf=xFormula.replace("$x","($x)")
  xf=xf.replace("$y","($y)")
  yf=yFormula.replace("$x","($x)")
  yf=yf.replace("$y","($y)")

  lsOut=[]
 # print xFormula, yFormula
  for line in ls:
     x=line[0]
     y=line[1]

     localxf = xf.replace("($x)",str(line[0]))
     localxf = localxf.replace("($y)",str(line[1]))
     localyf = yf.replace("($x)",str(line[0]))
     localyf = localyf.replace("($y)",str(line[1]))

     try:
#       print localxf
       lsOut.append(
           [ eval( localxf ), eval( localyf ) ]
       )

     except:

	sys.stderr.write("[PySPG.Load.TransformXY - ERR ] skipping line: "+str(line)+"\n")
  return lsOut

def splitListXY(ls):
  lsOutX = [ i[0] for i in ls ]
  lsOutY = [ i[1] for i in ls ]
  return lsOutX,lsOutY

def transformXYZ(ls,xFormula="$x",yFormula="$y",zFormula="$z"):
  xf=xFormula.replace("$x","($x)")
  xf=xf.replace("$y","($y)")
  xf=xf.replace("$z","($z)")
  yf=yFormula.replace("$x","($x)")
  yf=yf.replace("$y","($y)")
  yf=yf.replace("$z","($z)")
  zf=zFormula.replace("$x","($x)")
  zf=zf.replace("$y","($y)")
  zf=zf.replace("$z","($z)")

  lsOut=[]

  for line in ls:
     x=line[0]
     y=line[1]
     z=line[2]

     localxf = xf.replace("($x)",str(line[0]))
     localxf = localxf.replace("($y)",str(line[1]))
     localxf = localxf.replace("($z)",str(line[2]))

     localyf = yf.replace("($x)",str(line[0]))
     localyf = localyf.replace("($y)",str(line[1]))
     localyf = localyf.replace("($z)",str(line[2]))

     localzf = zf.replace("($x)",str(line[0]))
     localzf = localzf.replace("($y)",str(line[1]))
     localzf = localzf.replace("($z)",str(line[2]))


     try:

       lsOut.append(
           [ eval( localxf ), eval( localyf ) , eval( localzf ) ]
       )

     except:

	sys.stderr.write("err app)skipping line: "+str(line)+"\n")
  return lsOut

try:
 import numpy
except:
  import Numeric as numpy
#  sys.stderr.write("numpy Package Not found...\n")
#  sys.stderr.write("Not histogram capability present...\n")
else:
 def histogram(data, nbins,maxboxsize=10000,minx=-1e64,maxx=1e64):
  #
  # pythonize this code!!!!!!
  #
  if  len(data)==0:
    data=[0]

  mina=max(min(data),minx)
  maxa=min(max(data),maxx)
#  mina=min(data)
#  maxa=max(data)
  boxsize=min(maxboxsize,(maxa-mina)/nbins)
  out = [0]*int(math.ceil((maxa-mina)/boxsize))

  for idata in data:
    try:
      pos=int(math.floor((idata-mina)/boxsize))
      if pos == len(out):
        pos=len(out)-1
      sys.stderr.write("%d\n"%pos)
      out[pos]+=1
    except:

      sys.stderr.write("histogram error!!! len(data) = %d \n"%len(out))
      sys.stderr.write("\n".join([
				 "%s = %s"%(str(k),str(locals()[k]))
				 for k in locals().keys() if k is not "data"
			       ])+"\n"
                      )

      sys.exit()
  suma=numpy.sum(out)

  out3 = [
            x/suma for x in out
         ]
  out2 = []

  for i in range(nbins):
    out2.append( [float(i)/float(nbins)*(maxa-mina)+mina, out3[i] ] )
  return out2


def loadParamDat(paramFile):
  return [
     i.strip() for i in open(paramFile,"r").readlines() if i.strip()[0]!="%"
     ]


def filterDatasetX(ds,condicion):
  """
    la condicion es un string que devuelve una variable logica. Es funcion de y,i (el indice en la matriz de valores
  """
  ret = []
  i=0
  for dato in ds:
	x=dato
	if  not condicion or eval(condicion) :
	  ret.append(x)
	i+=1
  return ret

def filterDatasetXY(ds,condicion):
  """
    la condicion es un string que devuelve una variable logica. Es funcion de $x,$y,$i (el indice en la matriz de valores
  """
  if not condicion:
	return ds
  cond=condicion.replace("$x","($x)")
  cond=cond.replace("$y","($y)")
  cond=cond.replace("$i","($i)")
  ret = []
  i=0
  for dato in ds:
	x=dato[0]
	y=dato[1]
	localcond = cond.replace("($x)",str(x))
	localcond = localcond.replace("($y)",str(y))
	localcond = localcond.replace("($i)",str(i))
	if  eval(localcond) :
	  ret.append([x,y])
	i+=1
  return ret

