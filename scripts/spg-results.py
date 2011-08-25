#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:37:27 2011

@author: Claudio Tessone - <tessonec@ethz.ch>
"""

from spg.parameter import ResultsDBQuery
from spg.utils import generate_string
from spg.cmdline import BaseDBCommandParser

import os.path, os

import numpy as n


from spg.master import MasterDB

from spg import VAR_PATH, RUN_DIR

import sqlite3 as sql
import sys, optparse
import os, os.path


import fnmatch


class ResultsCommandParser(BaseDBCommandParser):
    """Results command handler"""
    
     parser.add_option("--table-depth", type="int", action='store', dest="table_depth",
                        default = 1, help = "The depth (how many independent variables) on the table are to be created")

     parser.add_option("--coalesce", type="string", action='store', dest="coalesce",
                        default = None, help = "comma separated list -with no blanks- ")

     parser.add_option("--prefix", type="string", action='store', dest="prefix",
                        default= "output", help = "prefix for the output")

     parser.add_option("--expand-dirs", action='store_true', dest="expand_dirs",
                        help = "whether to expand dirs instead of appending names to the output name")

     parser.add_option("--by-val", action='store_true', dest="by_val",
                        help = "whether to coalesce table by var -useful if repeated-")

     parser.add_option("--raw", action='store_true', dest="raw_data",
                        help = "whether to store all the data-points")

     parser.add_option("--split-cols", action='store_true', dest="split_columns",
                        help = "splits outputs column-wise")

#     parser.add_option("--filter","--insert", type="string", action='store',
 
    def __init__(self):
        BaseDBCommandParser.__init__(self)
        self.prompt = "| spg-results :::~ "
        
        self.expand_dirs = True 
        self.raw_data = False
        self.split_colums = False
        #        self.values = {'repeat': 1, 'sql_retries': 1, 'timeout' : 60, 'weight': 1}

#        self.doc_header = "default values: %s"%(self.values )





















#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()

     parser.add_option("--table-depth", type="int", action='store', dest="table_depth",
                        default = 1, help = "The depth (how many independent variables) on the table are to be created")

     parser.add_option("--coalesce", type="string", action='store', dest="coalesce",
                        default = None, help = "comma separated list -with no blanks- ")

     parser.add_option("--prefix", type="string", action='store', dest="prefix",
                        default= "output", help = "prefix for the output")

     parser.add_option("--expand-dirs", action='store_true', dest="expand_dirs",
                        help = "whether to expand dirs instead of appending names to the output name")

     parser.add_option("--by-val", action='store_true', dest="by_val",
                        help = "whether to coalesce table by var -useful if repeated-")

     parser.add_option("--raw", action='store_true', dest="raw_data",
                        help = "whether to store all the data-points")

     parser.add_option("--split-cols", action='store_true', dest="split_columns",
                        help = "splits outputs column-wise")

#     parser.add_option("--filter","--insert", type="string", action='store', dest="insert",
#                        help = "Inserts the given iterator before the first variable. The second argument is usually enclosed between quotes")

     return  parser.parse_args()


if __name__ == "__main__":
    opts, args = parse_command_line()
    
    for iarg in args:
    
       db_name = os.path.abspath( iarg )
    
       rq = ResultsDBQuery(db_name)
       output_cols = rq.output_column[1:]
       
       
       if opts.coalesce is not None:
          rq.coalesce = opts.coalesce.split(",")
       elif opts.table_depth is not None:
          rq.coalesce = rq.variables[:-opts.table_depth]
       for i in rq:
         if opts.split_columns:
           for column in output_cols:
              data = rq.result_table(restrict_to_values = i, raw_data = opts.raw_data, restrict_by_val = opts.by_val, output_column = [column] )
              if not opts.expand_dirs:
                 gen_s = generate_string(i, rq.coalesce )
                 output_fname = "%s_%s-%s.dat"%(opts.prefix, column,gen_s )
              else:
                 gen_s = generate_string(i, rq.coalesce, joining_string = "/" )
                 output_fname = "%s/%s-%s.dat"%(gen_s, opts.prefix  , column)
              d,f = os.path.split(output_fname)
              if d != "" and not os.path.exists(d):
                os.makedirs(d)
              n.savetxt( output_fname, data)
         else:
           data = rq.result_table(restrict_to_values = i, raw_data = opts.raw_data, restrict_by_val = opts.by_val)
          
           if not opts.expand_dirs:
              gen_s = generate_string(i, rq.coalesce )
              output_fname = "%s-%s.dat"%(opts.prefix, gen_s )
           else:
              gen_s = generate_string(i, rq.coalesce, joining_string = "/" )
              
              output_fname = "%s/%s.dat"%(gen_s, opts.prefix  )
           d,f = os.path.split(output_fname)
           if d != "" and not os.path.exists(d):
              os.makedirs(d)
           n.savetxt( output_fname, data)
             
  #  r1 = rq.result_table("ordprm_kuramoto")
  #  n.savetxt("ordprm_kuramoto",r1)
    
  #  r2 = rq.full_result_table()
  #  n.savetxt("output.dat",r2) 