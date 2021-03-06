#!/usr/bin/python
'''
Created on 12 Apr 2014

@author: tessonec
'''

import spg.plot as spgp
import spg.base as spgb 
import spg.utils as spgu



import sys
import os.path
import copy
import optparse
#from math import *


from spg import CONFIG_DIR

from spg.utils import newline_msg, evaluate_string


class SPGPlotter:

    def __init__(self, parameter_file):
        self.parameter_file = parameter_file
        
        self.mit = spgb.MultIteratorParser( open(parameter_file) )
        self.variables = self.mit.varying_items()
        
        
        self.settings, foo =  self.get_settings(self.mit.command, "inputs")
        
        settings_output, self.output_columns = self.get_settings(self.mit.command, "stdout")
        
        newline_msg( "INF", "output columns: %s"% enumerate(self.output_columns) )
        self.settings.update(settings_output)
        
        self.x_axis =  self.variables[-1]
        x_axis_iter = self.mit.data[ self.mit.position_of( self.x_axis ) ]
        if x_axis_iter.type == "*":
            
            self.add_setting( self.x_axis, "scale = log")
            self.add_setting( self.x_axis, "lim = (%s,%s)"%(x_axis_iter.xmin,x_axis_iter.xmax))
            
            
        
        try:
            self.coalesced_vars = [ self.variables[-2] ]
        except:
            self.coalesced_vars = []
            
        try:
            self.separated_vars = self.variables[:-2]
        except:
            self.separated_vars = []
        
        

    
    def get_settings(self, exec_file, part = "stdout"):
        """
         keysColumns = ["type","label","help","scale","repeat", "lim"]
         the structure of the columns in the files are as follows:
         name of the variable, and a colon separated list of -optional- options
         type:  of the plot if xy, one column is used, xydy two columns are used
         label: to be used in the plotting script
         scale: comma separated list of minimum and maximum values 
         repeat: how many columns are to be taken by the parser
         help: a string containing an explanation of the variable"""
         
        possible_keys = set(["type","label","help","scale","repeat","datatype", "lim"])
        if exec_file[:2] == "ct" and exec_file[3] == "-" :  exec_file = exec_file[4:]
        ret = {}
        exec_file,ext=os.path.splitext(exec_file)
    
        cfgFile = "%s/spg-conf/%s.%s"%(CONFIG_DIR,exec_file, part)
        
        sorted_cols = []
        for line in open(cfgFile):
            if len(line.strip()) == 0: continue
            
            l = [ i.strip() for i in line.split(":")]
            name = l.pop(0)
            
            sorted_cols.append(name)
            values = {} # {"type":"xy","datatype":"float"}
            
            for o in l:
                # print o, l
                k,v = o.split("=")
                k=k.strip()
                v=v.strip()
               
                if k not in possible_keys:
                    newline_msg("SYN","in column '%s', unrecognised key '%s'"%(name,k))
                    sys.exit(1)
                if k == "lim":
                    values[k] = eval(v)
                else:
                    values[k]=v
    
            ret[name] = values    
           
        return ret , sorted_cols
       
    
    
    def add_setting(self,  var, line):
        

        possible_keys = set(["type","label","help","scale","repeat","datatype", "lim"])
        
        if not self.settings.has_key(var):
            self.settings[ var ] = {}
        ret_name = self.settings[ var ]
        
        l = [ i.strip() for i in line.split(":")]
        for o in l:
            k,v = o.split("=")
            k=k.strip()
            v=v.strip()
              
            if k not in possible_keys:
                spgu.newline_msg("SYN","in column '%s', unrecognised key '%s'"%(name,k))
                
                sys.exit(1)
            if k == "lim":
                ret_name[k] = eval(v)
            else:
                ret_name[k]=v
 
    def setup_output_columns(self, oc):
        self.output_columns = oc
           

    def setup_coalesced_vars(self, cv):
        all_vars = self.separated_vars + self.coalesced_vars 
        for v in cv:
	  if v in all_vars:
	    all_vars.remove(v)
	self.coalesced_vars = cv
	self.separated_vars = all_vars


    def setup_separated_vars(self, sv):
        all_vars = self.separated_vars + self.coalesced_vars 
        for v in sv:
	  if v in all_vars:
	    all_vars.remove(v)
	self.coalesced_vars = all_vars
	self.separated_vars = sv

    def plot_all(self, Plotter):
        newline_msg( "INF", "%s - %s - %s"%(self.separated_vars, self.coalesced_vars, self.x_axis ) ) 

        table_name = self.parameter_file.replace("parameters","results")
        ctp = Plotter(table_name )
        
# ctp = spgp.SPGSubPlotter(table_name = "results-2a.dat")
        ctp.x_axis = self.x_axis

#ctp.y_axis = ['magnetisation', 'magnetisation_std', 'ordprm_potts', 'ordprm_potts_std',  'interface', 'interface_dyn']
        ctp.y_axis = self.output_columns 
# ctp.y_axis =  ['magnetisation',  'ordprm_potts', 'interface_dyn'] 
        
        ctp.separated_vars = self.separated_vars
        ctp.coalesced_vars = self.coalesced_vars


        ctp.settings = self.settings
#ctp.coalesced_vars = ['size']
#ctp.separated_vars = ['update_rate', 'rate_is']

#ctp.dict_of_vars = { 
#                    'update_rate':r'$\lambda$', 'size':r'$N$', 'rate_is':r'$\eta_i$', "diluted_p":r"$\rho$", 
#                    "magnetisation":r"$M$","ordprm_potts":r"$P$","interface_dyn":r"$I_d$",
#                    }
#ctp.dict_of_settings = { 'magnetisation': {'lim':(-0.05,1.05), 'scale':'log', 'label':r"$M$"},
#                         'diluted_p': {'lim':(-0.02,0.52), 'scale':'log','label':r"$\rho$"},
#                         'ordprm_potts': {'lim':(-0.05,1,05), 'scale':'log','label':r"$P$"}
#                        }
        plot_fname = table_name.replace("results","plot")[:-4]
        if len( ctp.separated_vars ) > 1:          
           plot_fname += "_"+"_".join( ctp.separated_vars )
        if len( ctp.separated_vars ) == 1:          
           plot_fname += "_"+ ctp.separated_vars [0]
        
        plot_fname += ".pdf"

        newline_msg( "OUT", plot_fname ) 
        ctp.plot_all(output_name = plot_fname)



#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser
    
     parser = OptionParser()

     parser.add_option("--coalesced", type="string", action='store', dest="coalesced", 
		        default = [],
                        help = "comma separated list of coalesced variables")

     parser.add_option("--separated", type="string", action='store', dest="separated", 
		        default = [],
                        help = "comma separated list of separated variables")
     parser.add_option("--output", type="string", action='store', dest="output", 
		        default = [],
                        help = "output structure")



     #parser.add_option("-a","--append", type="string", nargs=2, action='append', dest="append",
                        #help = "Appends the second iterator after the first variable. The second argument is usually enclosed between quotes")


     opts, args = parser.parse_args()
     if len( opts.coalesced ) >0:
         opts.coalesced = opts.coalesced.split(",")
     if len( opts.separated ) >0:
         opts.separated = opts.separated.split(",")
     if len( opts.output ) >0:
         opts.output = opts.output.split(",")
     return  opts, args 





import sys

opts, args = parse_command_line()

for iarg in args:
    
    plotter = SPGPlotter(iarg)
    if len(opts.coalesced) > 0:
        plotter.setup_coalesced_vars( opts.coalesced )
    if len(opts.separated) > 0:
        plotter.setup_separated_vars( opts.separated )
    if len(opts.output) > 0:
        plotter.setup_output_columns( opts.output )
    
    plotter.plot_all(spgp.SPGBasePlotter)

#plotter.coalesced_vars = "rate_is"
#plotter.separated_vars = "diluted_p"

#plotter.plot_all(spgp.SPGBasePlotter, "diluted_p")
