#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:37:27 2011

@author: Claudio Tessone - <tessonec@ethz.ch>
"""

from spg import VAR_PATH, RUN_DIR, CONFIG_DIR
import spg.utils as utils
from spg.cmdline import BaseDBCommandParser
from spg.master import MasterDB
from spg.parameter import ResultsDBQuery

from spg.plot import PyplotUnit, PyplotGraphicsUnit 


import numpy as np
import math as m
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.pylab as plb

import sqlite3 as sql
import sys, optparse
import os, os.path
import fnmatch


class ResultCommandParser(BaseDBCommandParser):
    """Results command handler"""

    def __init__(self):
        BaseDBCommandParser.__init__(self, EnsembleConstructor = ResultsDBQuery)
        self.prompt = "| spg-results :::~ "
        
        self.possible_keys = set( [ "table_depth", "expand_dirs", "raw_data", "split_colums", "restrict_by_val", "prefix", "n_rows", "plot_x_label", "plot_y_label", "plot_x_scale", "plot_y_scale", "plot_x_min", "plot_x_max", "plot_y_min", "plot_y_max"] )
        self.output_column = []
        self.table_depth = 1
        self.n_rows = 3
        self.expand_dirs = True 
        self.raw_data = False
        self.split_colums = False
        self.restrict_by_val = False # was True
        self.prefix = "output_"

        self.plot_x_label = ""
        self.plot_y_label = ""
        self.plot_x_scale = "linear"
        self.plot_y_scale = "linear"
        self.plot_x_min = None
        self.plot_x_max = None
        self.plot_y_min = None
        self.plot_y_max = None

        self.autoscale = None

        self.figures = {}
#        self.values = {'repeat': 1, 'sql_retries': 1, 'timeout' : 60, 'weight': 1}
#        self.doc_header = "default values: %s"%(self.values )

    def do_load(self,c):
        """loads a results_database"""
        BaseDBCommandParser.do_load(self, c)
        self.output_column = self.current_param_db.output_column[:]
        
        os.chdir( self.current_param_db.path )
        
  
    def do_save_table(c):
       """saves the table of values"""
       for i in self.current_param_db:
         if self.split_columns:
           for column in self.output_column:
              gen_d = utils.generate_string(i, self.separated_vars, joining_string = "/" )
              gen_s = utils.generate_string(i, self.coalesced_vars, joining_string = "_" )
              output_fname = "%s/%s-%s-%s.dat"%(gen_d, self.prefix, column, gen_s)
              d,f = os.path.split(output_fname)
              if d != "" and not os.path.exists(d): os.makedirs(d)
              data = self.current_param_db.result_table(restrict_to_values = i, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = [column] )
              np.savetxt( output_fname, data)
         else:
           data = self.current_param_db.result_table(restrict_to_values = i, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = self.output_column )
          
           gen_d = utils.generate_string(i, self.separated_vars, joining_string = "/" )
           gen_s = utils.generate_string(i, self.coalesced_vars, joining_string = "_" )
           output_fname = "%s/%s-%s.dat"%(gen_d, self.prefix, gen_s)
           d,f = os.path.split(output_fname)
           if d != "" and not os.path.exists(d): os.makedirs(d)
           np.savetxt( output_fname, data)

    def do_plot(self, c):
        """plots variables as a function of a parameter"""
        try:
            self.dict_of_params = utils.load_config( "%s/spg-conf/%s.params"%(CONFIG_DIR, self.current_param_db.executable[4:-3] ), "texlabel" )
        except: self.dict_of_params = {}
        try:
            self.dict_of_stdout = utils.load_config( "%s/spg-conf/%s.stdout"%(CONFIG_DIR, self.current_param_db.executable[4:-3] ), "texlabel" )
        except: self.dict_of_stdout = {}
#        for oc in self.figures.keys():
#             plt.close( self.figures[oc] )
        plt.clf() 
        self.figures = {}
        
        for i_restrict in self.current_param_db:
            fig_label = utils.generate_string(i_restrict, self.current_param_db.separated_vars, separator = "=", joining_string = " " )
            if not self.figures.has_key(fig_label):
                self.figures[ fig_label ] = PyplotGraphicsUnit(fig_label, self.n_rows, len(self.output_column) )
                for column in self.output_column:
                    self.figures[ fig_label ].add_subplot(column)
                    self.figures[ fig_label ].subplots[column].x_label = self.current_param_db.variables[-1]
                    self.figures[ fig_label ].subplots[column].y_label = column
                    self.figures[ fig_label ].subplots[column].x_scale = self.plot_x_scale
                    self.figures[ fig_label ].subplots[column].y_scale = self.plot_y_scale
                    self.figures[ fig_label ].subplots[column].x_range = (self.plot_x_min, self.plot_x_max)
                    self.figures[ fig_label ].subplots[column].y_range = (self.plot_y_min, self.plot_y_max)
                    self.figures[ fig_label ].subplots[column].refresh_style()
                    if self.dict_of_stdout.has_key(column):
                        self.figures[ fig_label ].subplots[column].plot_object.set_ylabel( self.dict_of_stdout[column] )
                    else:
                        self.figures[ fig_label ].subplots[column].plot_object.set_ylabel( column )
                    if self.dict_of_params.has_key(self.current_param_db.in_table_vars[0] ):
                        self.figures[ fig_label ].subplots[column].plot_object.set_ylabel( self.dict_of_params[ self.current_param_db.in_table_vars[0] ] )
                    else:
                        self.figures[ fig_label ].subplots[column].plot_object.set_params( self.current_param_db.in_table_vars[0] )
                        
            for column in self.output_column:#            self.figures[column] = plt.figure()
                curve_label = utils.generate_string(i_restrict, self.current_param_db.coalesced_vars, separator = "=", joining_string = " " )
                data = self.current_param_db.result_table(restrict_to_values = i_restrict, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = [column] )
#                print data
                self.figures[fig_label].subplots[column].add_curve( curve_label, data[:,0], data[:,1] )
                
        plt.show()
#        self.figures.clear()
#        for column in self.output_column:
#            self.figures[column] = plt.figure()
#            axes = self.figures[column].add_subplot(1,1,1)
#            for i in self.current_param_db:
#                data = self.result_table(restrict_to_values = i, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = [column] )
#                axes.plot( data, 'o' )
              
    def do_setup_vars_table(self,c):
        """sets up the table's independent columns"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        self.current_param_db.setup_output_table(c)

    def do_setup_vars_splitted(self,c):
        """sets up which variables are going to have a separated output"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        self.current_param_db.setup_separated_output(c)
        
        
    def do_setup_output_column(self,c):
        """sets which columns to generate output from"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        c = c.split(",")
        if not set(c).issubset(  self.current_param_db.output_column ):
            utils.newline_msg("ERR", "the column(s) is(are) not in the output: %s"%( set(c) - set(  self.current_param_db.output_column )) )
        self.output_column = c
            
    def do_set_as_var(self,c):
        """ Sets a (set of) non-variables as variable """
        if not self.current_param_db: 
            utils.newline_msg("WRN", "current db not set... skipping")
            return 
        ls_vars = c.split(",")
        if not set(ls_vars).issubset( set(self.current_param_db.entities) ):
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(ls_vars)-set(self.current_param_db.entities) )
            return
        for v in ls_vars:
            self.current_param_db.execute_query( 'UPDATE entities SET varies=1 WHERE name = ?', v)
        self.current_param_db.init_db()

    def do_set(self, c):
        """sets a VAR1=VALUE1[:VAR2=VALUE2]
        sets a value in the currently loaded database """
        
        if not self.current_param_db: 
            utils.newline_msg("WRN", "current db not set... skipping")
            return 
        
        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
        if not ret: 
            return
        for k in ret.keys():
            self.__dict__[k] = ret[k]

    def do_conf(self,c):
        """prints the current configuration"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        print " -- db: %s"%( self.shorten_name( self.current_param_db.full_name ) )
        print "  + variables = %s "%( ", ".join(self.current_param_db.variables ) )
        print "  + entities = %s "%( ", ".join(self.current_param_db.entities ) )
        print "  + columns = %s "%( ", ".join(self.current_param_db.output_column ) )
        print "  + split_colums = %s / expand_dirs = %s / raw_data = %s"%(self.split_colums, self.expand_dirs, self.raw_data)
        print "  + structure = %s - %s - %s / restrict_by_val = %s"%(self.current_param_db.separated_vars, self.current_param_db.coalesced_vars, self.current_param_db.in_table_vars, self.restrict_by_val)



        


##########################################################################################
##########################################################################################
#def parse_command_line():
#     from optparse import OptionParser
#
#     parser = OptionParser()
#
#     parser.add_option("--table-depth", type="int", action='store', dest="table_depth",
#                        default = 1, help = "The depth (how many independent variables) on the table are to be created")
#
#     parser.add_option("--coalesce", type="string", action='store', dest="coalesce",
#                        default = None, help = "comma separated list -with no blanks- ")
#
#     parser.add_option("--prefix", type="string", action='store', dest="prefix",
#                        default= "output", help = "prefix for the output")
#
#     parser.add_option("--expand-dirs", action='store_true', dest="expand_dirs",
#                        help = "whether to expand dirs instead of appending names to the output name")
#
#     parser.add_option("--by-val", action='store_true', dest="by_val",
#                        help = "whether to coalesce table by var -useful if repeated-")
#
#     parser.add_option("--raw", action='store_true', dest="raw_data",
#                        help = "whether to store all the data-points")
#
#     parser.add_option("--split-cols", action='store_true', dest="split_columns",
#                        help = "splits outputs column-wise")
#
##     parser.add_option("--filter","--insert", type="string", action='store', dest="insert",
##                        help = "Inserts the given iterator before the first variable. The second argument is usually enclosed between quotes")
#
#     return  parser.parse_args()


if __name__ == '__main__':
    cmd_line = ResultCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        


#
#if __name__ == "__main__":
#    opts, args = parse_command_line()
#    
#    for iarg in args:
#    
#       db_name = os.path.abspath( iarg )
#    
#       rq = ResultsDBQuery(db_name)
#       output_cols = rq.output_column[1:]
#       
#       
#       if opts.coalesce is not None:
#          rq.coalesce = opts.coalesce.split(",")
#       elif opts.table_depth is not None:
#          rq.coalesce = rq.variables[:-opts.table_depth]
#       for i in rq:
#         if opts.split_columns:
#           for column in output_cols:
#              data = rq.result_table(restrict_to_values = i, raw_data = opts.raw_data, restrict_by_val = opts.by_val, output_column = [column] )
#              if not opts.expand_dirs:
#                 gen_s = generate_string(i, rq.coalesce )
#                 output_fname = "%s_%s-%s.dat"%(opts.prefix, column,gen_s )
#              else:
#                 gen_s = generate_string(i, rq.coalesce, joining_string = "/" )
#                 output_fname = "%s/%s-%s.dat"%(gen_s, opts.prefix  , column)
#              d,f = os.path.split(output_fname)
#              if d != "" and not os.path.exists(d):
#                os.makedirs(d)
#              n.savetxt( output_fname, data)
#         else:
#           data = rq.result_table(restrict_to_values = i, raw_data = opts.raw_data, restrict_by_val = opts.by_val)
#          
#           if not opts.expand_dirs:
#              gen_s = generate_string(i, rq.coalesce )
#              output_fname = "%s-%s.dat"%(opts.prefix, gen_s )
#           else:
#              gen_s = generate_string(i, rq.coalesce, joining_string = "/" )
#              
#              output_fname = "%s/%s.dat"%(gen_s, opts.prefix  )
#           d,f = os.path.split(output_fname)
#           if d != "" and not os.path.exists(d):
#              os.makedirs(d)
#           n.savetxt( output_fname, data)
#             
  #  r1 = rq.result_table("ordprm_kuramoto")
  #  n.savetxt("ordprm_kuramoto",r1)
    
  #  r2 = rq.full_result_table()
  #  n.savetxt("output.dat",r2) 