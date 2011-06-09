#! /usr/bin/python
from numpy.random import uniform
from griddata import griddata
import pylab as p




PROGRAM_NAME         = "SPG-Coalesce"
PROGRAM_VERSION      = "0.1.0"
PROGRAM_AUTHOR       = "Claudio J. Tessone"
PROGRAM_RELEASE_DATE = "2011/03/25"
PROGRAM_EMAIL        = "tessonec@ethz.ch"

import spg.utils as spgu

import re, sys, shutil
import os.path, os


import numpy as n
#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()

     parser.add_option("-f","--file", type="string", action='store', dest="file_name", default = "out.dat",
                        help = "gives the name of the data file ")

     parser.add_option("--count", action='store_true', dest="count",
                        help = "gives the name of the variable to be stored in the merged file")

     #parser.add_option("--ycol", type="int", action='store', dest="ycol",default=0,
                        #help = "column to be considered containing the second independent axis")
     #parser.add_option("--zcol", type="int", action='store', dest="zcol",default=1,
                        #help = "column to be considered containing dependent axis")


     return  parser.parse_args()



opts, args = parse_command_line()



raw = n.loadtxt(opts.file_name)

x = raw[:,0]
y = raw[:,1]
z = raw[:,2]

sx = set()
for i in x:
  sx.add(i)
sy = set()
for i in y:
  sy.add(i)

nx = len(sx); ny = len(sy)
print nx, ny, x.min(), x.max(), y.min(), y.max()

xi, yi = p.meshgrid(p.linspace(x.min(),x.max(),nx),p.linspace(y.min(),y.max(),ny))
# masked=True mean no extrapolation, output is masked array.
zi = griddata(x,y,z,xi,yi,masked=True)

#print 'min/max = ',zi.min(), zi.max()

# Contour the gridded data, plotting dots at the nonuniform data points.
CS = p.contour(xi,yi,zi,15,linewidths=0.5,colors=['k'])
CS = p.contourf(xi,yi,zi,15,cmap=p.cm.jet)
p.colorbar() # draw colorbar

#p.xlim(-1.9,1.9)
#p.ylim(-1.9,1.9)
#p.title('griddata test (%d points)' % npts)
p.savefig(opts.file_name+".eps")
#p.show()
