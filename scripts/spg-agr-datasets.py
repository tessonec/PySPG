#!/usr/bin/python
# -*- coding: utf-8 -*-

# :::~ Author: Claudio Juan Tessone <tessonec@ethz.ch> (c) 2010
###
### 
###
###
# Distributed According to GNU Generic Purpose License (GPL) version 3
# Please visit www.gnu.org
###############################################################################

PROGRAM_NAME         = "CTP-AGR-Files"
PROGRAM_VERSION      = "0.2.0"
PROGRAM_AUTHOR       = "Claudio J. Tessone"
PROGRAM_RELEASE_DATE = "2010/05/18"
PROGRAM_EMAIL        = "tessonec@ethz.ch"

import sys, os, os.path, glob, re

import numpy
from math import *

  




def string_evaluator(string,val_dict):
      #fp = string # os.path.abspath(string)
      rx = re.compile(r'\{([a-zA-Z]\w*)\}')
      # regular expression explanation
      # r'\{(\w)\}' matches variable name: 

      #vars = set()
      st_out = string
      for i_var in rx.findall(string):
         #vars.add(i)
         st_out = re.sub( r'\{%s\}'%i_var, str(val_dict[i_var]), st_out )
         #print st_out
      return eval(st_out)



def parameter_guess(string):
      #fp = string # os.path.abspath(string)
      regexp = re.compile(r'([a-zA-Z]\w+)-([-+]?\d*\.?\d*){1,1}([Ee][+-]?\d+)?')
      # regular expression explanation
      # r'([a-zA-Z]\w+)' matches variable name: 
      #     :::~ begins with a letter, any combination of letters, numbers and undezrscores
      # r'-' matches separator: minus sign
      # r'([-+]?\d*\.?\d*){1,1}'
      #     :::~ decimal part
      # r'([Ee][+-]?\d+)?'
      #     :::~ exponent
      ret = {}
      for var, dec, exp in regexp.findall(string):
        if "" not in [var,dec]:
          try:
            ret[var] = int(dec+exp)
          except:
            ret[var] = float(dec+exp)
      return ret
 
#########################################################################################
#########################################################################################
#########################################################################################
def inlineMessage( type, msg ):
  print >> sys.stderr, "[%s - %5s ] %s...\r"%(os.path.split(sys.argv[0])[1], type, msg),
  sys.stderr.flush()

def newlineMessage( type, msg ):
  print >> sys.stderr, "[%s - %5s ] %s"%(os.path.split(sys.argv[0])[1], type, msg)
  sys.stderr.flush()
#########################################################################################
#########################################################################################


def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()
     
     parser.add_option("--hspace", dest="h_space",type="int",default=12,
                       help="Space between columns in the plots ")

     parser.add_option("--vspace", dest="v_space",type="int",default=12,
                       help="Space between rows in the plots")

     parser.add_option("--xcol", dest="x_col",type="int",default=0,
                       help="The default column to extract the x data from")

     parser.add_option("--ycol", dest="y_col",type="int",default=0,
                       help="The default column to extract the y data from")

     parser.add_option("--xtransform", dest="x_transform",type="string",default=None,
                       help="The transformation formula to apply to the x-axis")

     parser.add_option("--ytransform", dest="y_transform",type="string",default=None,
                       help="The transformation formula to apply to the y-axis")

     parser.add_option("--template", dest="template",type="string",default=None,
                       help="The filename that contains an AGR template ")

     parser.add_option("-o","--output", dest="output",type="string",default="output.agr",
                       help="The output filename ")

     parser.add_option("-i","--input", dest="default_file_name",type="string",default=None,
                       help="The default input file")
     
     parser.add_option("-g","--geometry", dest="geometry",type="string",default=None,
                       help="The array to place the plots in")

     parser.add_option("--autoscale", dest="auto_scale",action="store_true",
                       help="auto-scales all the plots.")

     parser.add_option("-s", "--skip", dest="skip",type="int",default=1,
                       help="Number  +1  of lines it skips between outputs")

     parser.add_option("--xlabel", dest="xlabel",type="string",default="",
                       help="label for all the x axes")

     parser.add_option("--ylabel", dest="ylabel",type="string",default="",
                       help="label for all the y axes")

     parser.add_option("--scale", dest="scale",type="string",default=None,
                       help="range for the axes comma separated list written as xmin,ymin,xmax,ymax ")

     parser.add_option("--scale-ticks", dest="scale_ticks",type="string",default=None,
                       help="ticks  for the axes comma separated list written as xticks,yticks ")

     parser.add_option("-l","--log",dest="logarithmic_scale",type="string",default="",
                       help="the axes to set in logarithmic scale")



     
     return  parser.parse_args()





class DataConf:
  default_x_col = 0
  default_y_col = 1
  
  default_file_name = None
  default_plot = [0]
  
  def unfold(self):
    if len(self.x_col) == 1:
       ret = [self]
    else:
       ret = []
       for i in range(len( self.x_col )):
	 aux = DataConf()
	 aux.file_name = self.file_name
	 aux.x_col = self.x_col[i]
	 aux.y_col = self.y_col[i]
	 aux.plot = self.plot[i]
	 ret.append(aux)

    ret2 = []
    for dc in ret:
	 #ls_files = glob.glob(dc.filename)
	 #print glob.glob(dc.file_name)
         for file in sorted( glob.glob(dc.file_name) ):
	   aux = DataConf()
	   aux.file_name = file
	   aux.x_col = dc.x_col
	   aux.y_col = dc.y_col
	   aux.plot = dc.plot
	   ret2.append(aux)
	    
    return ret2


  def __init__(self, s = ""):
    self.x_col = [ self.default_x_col ]
    self.y_col = [ self.default_y_col ]
    self.file_name = self.default_file_name
    self.plot = self.default_plot
    #print s.split(':')
    for i_k in s.split(':'):
        #print i_k
	try:
	  if i_k.find("=") == -1:
	    self.file_name = i_k
	    continue
	  [k,v] = i_k.split("=")
	  #print k,v
          if k =="file":
            self.file_name = v
          elif k =="plot":
	      self.plot = map( int,v.split(',') )
          elif k =="x":
	      self.x_col = map( int,v.split(',') )
          elif k =="y":
	      self.y_col = map( int,v.split(',') )
          else:
	    raise Exception("error")
        except:
          newlineMessage( "ERROR", 'while parsing "%s" argument'%i_k)	  
	  sys.exit(2)
        #print self.plot , self.x_col , self.y_col 

    if len( self.x_col ) == 1 and len( self.y_col ) > 1:
	   xaux = self.x_col[0] 
	   self.x_col = [ xaux for i in range( len(self.y_col) ) ]
    elif len( self.x_col ) != len( self.y_col ) and  len( self.x_col )>1: 
           newlineMessage( "ERROR", 'x,y inconsistent in "%s" argument'%s)	  
	   sys.exit(3)

    #print self.plot , self.x_col , self.y_col 
    if len( self.plot ) == 1 and len( self.y_col ) > 1:
	   xaux = self.plot[0] 
	   self.plot = [ xaux for i in range( len(self.y_col) ) ]
    elif len( self.plot ) != len( self.y_col ) :
	   newlineMessage( "ERROR", 'plots,y inconsistent in "%s" argument'%s)	  
	   sys.exit(4)
         
  def __str__(self):
     return '%s: ( %s, %s) in graphs: %s'%( self.file_name ,self.x_col, self.y_col, self.plot) 


options, args = parse_command_line()

DataConf.default_x_col = options.x_col
DataConf.default_y_col = options.y_col
DataConf.default_file_name = options.default_file_name 


vec_final = []


for dc in [DataConf(arg) for arg in args]:
  #print dc.unfold()
  vec_final.extend( dc.unfold() )

fout = open(options.output,"w")


if options.geometry is not None:
  [arr_x , arr_y ] = map(int, options.geometry.split("x") )

  if arr_x > 1:  
    print >> fout, "@page size %d,%d"%(arr_y *800 , arr_x*480)
  else:
    print >> fout, "@page size %d,%d"%(arr_y *1024 , arr_x*768)

  print >> fout, "@arrange(%s, %s, 0.%d, 0.%d, 0.%d)"%(arr_x , arr_y, options.h_space, options.h_space, options.v_space)

if options.template is not None:
  print >> fout, "\n".join( open( options.template, "r" ).readlines() )    





dic_ac = {}
for ds in vec_final:
  if ds.plot[0] not in dic_ac.keys():
    dic_ac[ds.plot[0]] = 0
  else:
    dic_ac[ds.plot[0]] += 1
  print >> fout, "@with g%d"%ds.plot[0]
  print >> fout, "@ xaxis  label \"%s\""%options.xlabel  
  print >> fout, "@ yaxis  label \"%s\""%options.ylabel
  if "x" in options.logarithmic_scale.lower():  
    print >> fout, "@    xaxes scale Logarithmic"
  if "y" in options.logarithmic_scale.lower():  
    print >> fout, "@    yaxes scale Logarithmic"
  if options.scale:
    print >> fout, "@    world %s"% ( ", ".join( options.scale.strip("\"\'" ).split(",") ) )
  if options.scale_ticks:
    tcks = options.scale_ticks.strip("\"\'" ).split(",")
    print >> fout, "@     xaxis  tick major %s"% ( tcks[0] )
    print >> fout, "@     yaxis  tick major %s"% ( tcks[1] )

  
  data = numpy.loadtxt(  ds.file_name, usecols=(ds.x_col[0] , ds.y_col[0] )  )
  dic_vals = parameter_guess( os.path.abspath( ds.file_name ) )
  irow = 0

  
  print >> fout, "@target g%d.s%d"%( ds.plot[0], dic_ac[ds.plot[0]] )
  print >> fout, "@type xy"
  for [x,y] in data:
    irow+=1
    if irow % options.skip != 0:
      continue
    dic_vals['x'] =  x
    dic_vals['y'] =  y
    if options.x_transform:
      x =  string_evaluator(options.x_transform,dic_vals)
    if options.y_transform:
      y =  string_evaluator(options.y_transform,dic_vals)
    print >> fout, x,y
  print >> fout, "&"


#     parser.add_option("--xlabel", dest="xlabel",type="string",default="",
#                       help="label for all the x axes")
#     parser.add_option("--xrange", dest="xrange",type="string",default=None,
#                       help="label for all the x axes")
#     parser.add_option("-l","--log",dest="logarithmic_scale",type="string",default="",
#                       help="the axes to set in logarithmic scale")
#@    world 5, -1.2, 50000, 1.2
#@    xaxes scale Logarithmic


  if options.auto_scale:
    q >> fout, "@autoscale  "

  
