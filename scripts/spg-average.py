#!/usr/bin/env python

import numpy as np
from optparse import OptionParser
import sys


######################################################################
######################################################################

def average_file(fin, xcolumn = 0, ycolumn = False, keep_maximum=False):
  """
    computes the averages in fin.
    xcolumn: is the position of the column selected as x value
    ycolumn: is the column y, or a vector indicating the columns to be averaged
    keep_maximum: specifies whether the average is computed 
        over the maximum count of a particular value
  """
  data_dict={}
  n_dict={}
  keys=set()

  for line in open(fin,"r"):
    data = np.array( map(float, line.split()) )

    x = data[ xcolumn ]
    if ycolumn:
      data = data[ ycolumn ]

    if x in keys:
      n_dict[x] += 1.
      data_dict[x] += data
    else:
      n_dict[x] = 1.
      data_dict[x] = data
      keys.add(x)

  key_list = [ i for i in keys ]
  key_list.sort()

  if not keep_maximum:
    if ycolumn:
      return [ data_dict[x]/n_dict[x] for x in key_list ]
    else:
      return [ data_dict[x]/n_dict[x] for x in key_list ]
  else:
    nreal=max( n_dict.values() )
    if ycolumn:
      return [ data_dict[x]/nreal for x in key_list ]
    else:
      return [ data_dict[x]/nreal for x in key_list ]



######################################################################
######################################################################


parser = OptionParser()

parser.add_option("-x","--xcol", dest="xcol", type="int", default=0, 
                   help="sets the position of the column with the x data")
parser.add_option("-y","--ycol", dest="ycol", type="string", default="all",
                   help="sets the position of the column with the y data, it also accepts a comma separated list of columns to be averaged")
parser.add_option("-k","--keep", dest="keep_maximum", action="store_true")

(options, args) = parser.parse_args()

if options.ycol == "all":
  options.ycol = False
else:
  options.ycol = map(int, options.ycol.split(","))
  if options.xcol not in options.ycol:
    options.ycol.insert(0,options.xcol)
# print "selected ycol=", options.ycol
for i_arg in args:
  print >> sys.stderr, "[%s - MSG] averaging '%s'... "%(sys.argv[0],i_arg)
  data = average_file(i_arg, options.xcol, options.ycol, options.keep_maximum)
  fout = open(i_arg+".mean","w")
  for d in data:
    print >> fout, "\t".join( [str(i) for i in d ])

