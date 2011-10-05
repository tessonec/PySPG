'''
Created on Oct 5, 2011

@author: tessonec
'''

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



class PlotCommandParser(BaseDBCommandParser):
    """Results command handler"""

    def __init__(self):
        BaseDBCommandParser.__init__(self, EnsembleConstructor = ResultsDBQuery)
        self.prompt = "| spg-results :::~ "
        
        self.possible_keys = set( [ "table_depth", "expand_dirs", "raw_data", "split_colums", "restrict_by_val", "prefix", "n_rows", "plot_x_label", "plot_y_label", "plot_x_scale", "plot_y_scale", "plot_x_min", "plot_x_max", "plot_y_min", "plot_y_max", "split_columns"] )
        self.output_column = []
        self.table_depth = 1
        self.n_rows = 3
        self.expand_dirs = True 
        self.raw_data = False
        self.split_columns = False
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
        
  
    def __plot(self):
        try:
            self.dict_of_params = utils.load_config( "%s/spg-conf/%s.params"%(CONFIG_DIR, self.current_param_db.command[4:-3] ), "texlabel" )
        except: self.dict_of_params = {}
        try:
            self.dict_of_stdout = utils.load_config( "%s/spg-conf/%s.stdout"%(CONFIG_DIR, self.current_param_db.command[4:-3] ), "texlabel" )
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
                    print  column, self.n_rows, len(self.output_column)
                    self.figures[ fig_label ].add_subplot(column)
                    self.figures[ fig_label ].subplots[column].x_label = self.current_param_db.variables[-1]
                    self.figures[ fig_label ].subplots[column].y_label = column
                    self.figures[ fig_label ].subplots[column].x_scale = self.plot_x_scale
                    self.figures[ fig_label ].subplots[column].y_scale = self.plot_y_scale
                    self.figures[ fig_label ].subplots[column].x_range = (self.plot_x_min, self.plot_x_max)
                    self.figures[ fig_label ].subplots[column].y_range = (self.plot_y_min, self.plot_y_max)
                    self.figures[ fig_label ].subplots[column].refresh_style()
                    if self.dict_of_stdout.has_key(column):
                        self.figures[ fig_label ].subplots[column].plot_object.set_ylabel( "$%s$"%self.dict_of_stdout[column] )
                    else:
                        self.figures[ fig_label ].subplots[column].plot_object.set_ylabel( "$%s$"%column )
                    if self.dict_of_params.has_key(self.current_param_db.in_table_vars[0] ):
                        self.figures[ fig_label ].subplots[column].plot_object.set_xlabel( "$%s$"%self.dict_of_params[ self.current_param_db.in_table_vars[0] ] )
                    else:
                        self.figures[ fig_label ].subplots[column].plot_object.set_xlabel( "$%s$"%self.current_param_db.in_table_vars[0] )
                        
            for column in self.output_column:#            self.figures[column] = plt.figure()
                curve_label = utils.generate_string(i_restrict, self.current_param_db.coalesced_vars, separator = "=", joining_string = " " )
                data = self.current_param_db.result_table(restrict_to_values = i_restrict, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = [column] )
#                print data
                self.figures[fig_label].subplots[column].add_curve( curve_label, data[:,0], data[:,1] )
                

    def do_plot(self, c):
        """plots variables as a function of a parameter"""
        self.__plot()
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
        
        
    def do_plot_save(self, c):
        """plots variables as a function of a parameter"""
        if not c:
            c = "eps"
        self.__plot()        
        for f_lab in self.figures.keys():
            self.figures[f_lab].figure.savefig("%s.%s"%(f_lab,c))
                

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
        print "  + split_columns = %s / expand_dirs = %s / raw_data = %s"%(self.split_columns, self.expand_dirs, self.raw_data)
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
    cmd_line = PlotCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        
