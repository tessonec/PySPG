#!/usr/bin/python
'''
Created on 12 Apr 2014

@author: tessonec
'''

import spg.plot as spgp
import spg.base as spgb 
import spg.utils as spgu


import pandas as pd

import os.path


import ipywidgets as ipyw
import itertools

import matplotlib.pyplot as plt
import matplotlib.lines as mpll

from IPython.display import display



from spg import CONFIG_DIR

# from spg.utils import newline_msg, evaluate_string, load_configuration

from spg.plot import DataFrameIterator

class SPGDataLoader:
    """
     A class that constructs the plots.
     It exposes
     self.parameter_file: spg file name
     self.base_name:
     self.datafile_name:

     self.simulation: the MultIterator that describes the simulation

     self.full_dataframe : ALl the data in the table
     self.variables
     self.constants
    """

    def __init__(self, simulation_filename, table_name ="results"):

        self.simulation = spgb.MultIteratorParser(open(simulation_filename))

        self.simulation_filename = simulation_filename

        self.base_name, foo = os.path.splitext(self.simulation_filename)
        self.datafile_name = "%s_%s.csv"%(self.base_name, table_name)

        self.variables = self.simulation.varying_items()

        try:
            self.settings, foo =  spgu.load_configuration( "%s.input"%self.base_name )
        except:
            self.settings = spgu.SPGSettings()
            spgu.newline_msg( "INF", "no 'input' file found: %s"%self.simulation.command)

        settings_output, self.output_columns = spgu.load_configuration( "%s.stdout"%self.simulation.command.split(".")[0] )
        
        spgu.newline_msg( "INF", "output columns: %s"% self.output_columns)
        self.settings.update(settings_output)
        
        self.independent_var =  self.variables[-1]

        x_axis_iter = self.simulation.data[ self.simulation.position_of(self.independent_var)]
        if not self.settings.has_key( self.independent_var ):
            self.settings[ self.independent_var ] = spgu.SPGSettings()
        if x_axis_iter.type == "*":
            self.settings[self.independent_var]['scale'] = 'log'
            self.settings[self.independent_var]['lim'] =  (x_axis_iter.xmin, x_axis_iter.xmax)

        try:
            self.coalesced_vars = [ self.variables[-2] ]
        except:
            self.coalesced_vars = []
            
        try:
            self.separated_vars = self.variables[:-2]
        except:
            self.separated_vars = []


        self.full_dataframe = pd.read_csv(self.datafile_name)

        self.constants = {}
        for vn in self.full_dataframe.keys():
            if vn in self.variables:
                continue
            self.constants[vn] = self.full_dataframe[vn].unique()[0]

        self.data = self.full_dataframe[self.variables + self.output_columns]


    def describe_variables(self):
        for v in self.variables:
            red_d = self.data[ v ].unique()
            print "%-16s: %4s values || %s -- %s"%(v, len(red_d), min(red_d), max(red_d) )


    def describe_configuration(self):
        print "variables      : %s"%( ", ".join(self.variables ) )
        print "  + separated  : %s"%(self.separated_vars)
        print "  + coalesced  : %s"%(self.coalesced_vars)
        print "  + independent: %s"%(self.independent_var)
        print "output columns : %s "%( ", ".join(self.output_columns) )




    def setup_output_columns(self, oc):
        self.output_columns = oc
        self.data = self.full_dataframe[self.variables + self.output_columns]


    def setup_coalesced_vars(self, cv):
        all_vars = self.separated_vars + self.coalesced_vars
        for v in cv:
            if v in all_vars or v == self.independent_var:
                all_vars.remove(v)
        self.coalesced_vars = cv
        self.separated_vars = all_vars


    def setup_separated_vars(self, sv):
        all_vars = self.separated_vars + self.coalesced_vars
        for v in sv:
            if v in all_vars or v == self.independent_var:
                all_vars.remove(v)
        self.coalesced_vars = all_vars
        self.separated_vars = sv

    def setup_independent_var(self, v):
        if v in self.coalesced_vars:
            self.coalesced_vars.remove(v)
            self.independent_var = v
        if v in self.separated_vars:
            self.separated_vars.remove(v)
            self.independent_var = v





    #
    # def get_settings(self, exec_file, part = "stdout"):
    #     """
    #      keysColumns = ["type","label","help","scale","repeat", "lim"]
    #      the structure of the columns in the files are as follows:
    #      name of the variable, and a colon separated list of -optional- options
    #      type:  of the plot if xy, one column is used, xydy two columns are used
    #      label: to be used in the plotting script
    #      scale: comma separated list of minimum and maximum values
    #      repeat: how many columns are to be taken by the parser
    #      help: a string containing an explanation of the variable"""
    #
    #     possible_keys = set(["type","label","help","scale","repeat","datatype", "lim"])
    #     ret = {}
    #     exec_file,ext=os.path.splitext(exec_file)
    #     try:
    #         cfgFile = "%s.%s"%(exec_file, part)
    #     except:
    #         cfgFile = "%s/%s.%s" % (CONFIG_DIR, exec_file, part)
    #     sorted_cols = []
    #     for line in open(cfgFile):
    #         if len(line.strip()) == 0: continue
    #
    #         l = [ i.strip() for i in line.split(":")]
    #         name = l.pop(0)
    #
    #         sorted_cols.append(name)
    #         values = {} # {"type":"xy","datatype":"float"}
    #
    #         for o in l:
    #             # print o, l
    #             k,v = o.split("=")
    #             k=k.strip()
    #             v=v.strip()
    #
    #             if k not in possible_keys:
    #                 spgu.newline_msg("SYN","in column '%s', unrecognised key '%s'"%(name,k))
    #                 sys.exit(1)
    #             if k == "lim":
    #                 values[k] = eval(v)
    #             else:
    #                 values[k]=v
    #
    #         ret[name] = values
    #
    #     return ret , sorted_cols
       
    
    
    # def add_setting(self,  var, line):
    #
    #     possible_keys = set(["type","label","help","scale","repeat","datatype", "lim"])
    #
    #     if not self.settings.has_key(var):
    #         self.settings[ var ] = {}
    #     ret_name = self.settings[ var ]
    #
    #     l = [ i.strip() for i in line.split(":")]
    #     for o in l:
    #         k,v = o.split("=")
    #         k=k.strip()
    #         v=v.strip()
    #
    #         if k not in possible_keys:
    #             spgu.newline_msg("SYN","in column '%s', unrecognised key '%s'"%(var,k))
    #
    #             sys.exit(1)
    #         if k == "lim":
    #             ret_name[k] = eval(v)
    #         else:
    #             ret_name[k]=v


    def cycle_all(self, f_local):

        ret = []
        for outer_df in DataFrameIterator( self.data, self.separated_vars ):
            for inner_df in DataFrameIterator( outer_df, self.coalesced_vars ):

                r_loc = f_local(outer_df, inner_df )
                ret.append(r_loc)
        return ret

    def get_separated_values(self):

        ret = []
        for outer_df in DataFrameIterator(self.data, self.separated_vars):
            #            for inner_df in DataFrameIterator( outer_df, self.coalesced_vars ):
            ret.append( [ outer_df[v].unique()[0] for v in self.separated_vars ] )
        return ret

    def get_coalesced_values(self):

        ret = []
        for inner_df in DataFrameIterator(self.data, self.coalesced_vars):
            #            for inner_df in DataFrameIterator( outer_df, self.coalesced_vars ):
            ret.append( [ inner_df[v].unique()[0] for v in self.coalesced_vars ] )

        return ret



    def outer_inner(self, outer_df, inner_df):
        ouv = [ outer_df[v].unique()[0] for v in self.separated_vars ]
        iuv = [ inner_df[v].unique()[0] for v in self.coalesced_vars ]

#        ouv = ", ".join( [ "%s"%(outer_df[v].unique()[0]) for v in self.separated_vars ] )
#        iuv = ", ".join( [ "%s"%(inner_df[v].unique()[0]) for v in self.coalesced_vars ] )

        return ouv, iuv

    #
    # def plot_all(self, Plotter):
    #     spgu.newline_msg("INF", "%s - %s - %s" % (self.separated_vars, self.coalesced_vars, self.independent_var))
    #
    #     table_name = self.base_name + "_results.csv"
    #     ctp = Plotter(table_name)
    #
    #     ctp.x_axis = self.independent_var
    #
    #     ctp.y_axis = self.output_columns
    #
    #     ctp.separated_vars = self.separated_vars
    #     ctp.coalesced_vars = self.coalesced_vars
    #
    #     ctp.settings = self.settings
    #
    #     plot_fname = self.base_name + "_plot"
    #     if len(ctp.separated_vars) > 1:
    #         plot_fname += "_" + "_".join(ctp.separated_vars)
    #     if len(ctp.separated_vars) == 1:
    #         plot_fname += "_" + ctp.separated_vars[0]
    #
    #     plot_fname += ".pdf"
    #
    #     spgu.newline_msg("OUT", plot_fname)
    #     ctp.plot_all(output_name=plot_fname)
    #
    #
    # def plot_all_join_outputs(self, Plotter):
    #     spgu.newline_msg("INF", "%s - %s - %s" % (self.separated_vars, self.coalesced_vars, self.independent_var))
    #
    #     table_name = self.base_name + "_results.csv"
    #     ctp = Plotter(table_name)
    #
    #     ctp.x_axis = self.independent_var
    #
    #     ctp.y_axis = self.output_columns
    #
    #     ctp.separated_vars = self.separated_vars
    #     ctp.coalesced_vars = self.coalesced_vars
    #
    #     ctp.settings = self.settings
    #
    #     plot_fname = self.base_name + "_plot"
    #     if len(ctp.separated_vars) > 1:
    #         plot_fname += "_" + "_".join(ctp.separated_vars)
    #     if len(ctp.separated_vars) == 1:
    #         plot_fname += "_" + ctp.separated_vars[0]
    #
    #     plot_fname += ".pdf"
    #
    #     spgu.newline_msg("OUT", plot_fname)
    #     ctp.plot_all_join_outputs(output_name=plot_fname)


class InteractivePlotter:

        colors = ['black', 'blue', 'green', 'red', 'yellow', 'brown', 'grey', 'violet']
        markers = mpll.Line2D.filled_markers

        def __init__(self, splotter):
            # self.splotter = splotter

            self.full_data = splotter.data

            self.separated_values = splotter.get_separated_values()
            self.separated_vars = splotter.separated_vars
            self.separated_selection = self.separated_values[0]

            self.coalesced_values = splotter.get_coalesced_values()
            self.coalesced_vars = splotter.coalesced_vars

            self.output_columns = splotter.output_columns
            self.dependent_var = self.output_columns[0]

            self.independent_var = splotter.independent_var
            self.figure, self.axis = plt.subplots(1, 1, figsize=(12, 6))

            self.settings = splotter.settings

            vec_labels = [(", ".join(map(str, ou)), ou) for ou in self.separated_values]

            self.dd_filter = ipyw.Dropdown(
                options=vec_labels)  # ,
            # description = "%s :"%(self.separated_vars) )
            self.dd_output = ipyw.Dropdown(
                options=self.output_columns)  # ,

            self.select_xscale = ipyw.Checkbox(
                value=False,
                description='x log scale',
                icon='check'
            )

            self.select_yscale = ipyw.Checkbox(
                value=False,
                description='y log scale',
                icon='check'
            )

            # description = "Output columns: ")

            self.dd_filter.observe(self.on_dd_filter_value_change, names='value')
            self.dd_output.observe(self.on_dd_output_value_change, names='value')

            self.select_yscale.observe(self.on_select_scale, names=['value', 'owner'])
            self.select_xscale.observe(self.on_select_scale, names=['value', 'owner'])

            self.__separated_value_change()
            display(
                ipyw.HBox([
                    ipyw.HBox([ipyw.Label("%s: " % (self.separated_vars)), self.dd_filter]),
                    ipyw.HBox([ipyw.Label("Output columns: "), self.dd_output])
                ]),
                ipyw.HBox([self.select_xscale, self.select_yscale])
            )
            self.draw()

        def __separated_value_change(self):
            query_str = " & ".join(["(%s==%s)" % i for i in zip(self.separated_vars, self.separated_values)])
            if len(query_str) > 0:
                self.data = self.full_data.query(query_str)
            else:
                self.data = self.full_data

        def on_select_scale(self, change):

            #     if not change.has_key('new'): return
            if change['owner'] == self.select_xscale:
                xscale = "log" if change['new'] else "linear"
                print xscale
                self.axis.set_xscale(xscale)
            if change['owner'] == self.select_yscale:
                yscale = "log" if change['new'] else "linear"
                self.axis.set_yscale(yscale)
            self.axis.figure.canvas.draw()

        def on_dd_filter_value_change(self, change):
            self.separated_values = change['new']
            self.__separated_value_change()
            self.redraw()

        def on_dd_output_value_change(self, change):
            self.dependent_var = change['new']

            self.redraw()

        def redraw(self):
            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)

            for ix, iv in enumerate(self.coalesced_values):
                query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
                local_df = self.data.query(query_inn_str)

                self.axis.lines[ix].set_data(local_df[self.independent_var], local_df[self.dependent_var])

            self.axis.set_ylim(min(self.data[self.dependent_var]), max(self.data[self.dependent_var]))
            self.axis.set_xlim(min(self.data[self.independent_var]), max(self.data[self.independent_var]))
            self.axis.set_xlabel(self.independent_var)
            self.axis.set_ylabel(self.dependent_var)
            self.axis.figure.canvas.draw()

        def draw(self):

            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)
            for iv in self.coalesced_values:
                query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
                local_df = self.data.query(query_inn_str)
                self.axis.plot(local_df[self.independent_var], local_df[self.dependent_var],
                               linestyle='', marker=marker_it.next(), color=color_it.next(),
                               label=query_inn_str)

            self.axis.set_ylim(min(self.data[self.dependent_var]), max(self.data[self.dependent_var]))
            self.axis.set_xlim(min(self.data[self.independent_var]), max(self.data[self.independent_var]))
            self.axis.set_xlabel(self.independent_var)
            self.axis.set_ylabel(self.dependent_var)

            box = self.axis.get_position()
            self.axis.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            self.axis.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            if self.settings.has_key(self.independent_var):
                # print self.settings[curr_y_axis],
                if self.settings[self.independent_var].has_key('lim'):
                    self.axis.set_ylim(self.settings[self.independent_var]['lim'])
                if self.settings[self.independent_var].has_key('scale'):
                    self.select_xscale.value = self.settings[self.independent_var]['scale'] == 'log'
            if self.settings.has_key(self.dependent_var):
                if self.settings[self.dependent_var].has_key('lim'):
                    plt.axis.set_ylim(self.settings[self.y_axis]['lim'])
                if self.settings[self.dependent_var].has_key('scale'):
                    self.select_yscale.value = self.settings[self.dependent_var]['scale'] == 'log'

            self.axis.figure.canvas.draw()


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
                       default=[],
                       help="output structure")

     parser.add_option("--join", action='store_true', dest="join",
                       default=[],
                       help="join all y columns")

     opts, args = parser.parse_args()
     if len( opts.coalesced ) >0:
         opts.coalesced = opts.coalesced.split(",")
     if len( opts.separated ) >0:
         opts.separated = opts.separated.split(",")
     if len( opts.output ) >0:
         opts.output = opts.output.split(",")
     return  opts, args 





if __name__ == "__main__":
    opts, args = parse_command_line()

    for iarg in args:
    
        plotter = SPGDataLoader(iarg)
        if len(opts.coalesced) > 0:
            plotter.setup_coalesced_vars( opts.coalesced )
        if len(opts.separated) > 0:
            plotter.setup_separated_vars( opts.separated )
        if len(opts.output) > 0:
            plotter.setup_output_columns( opts.output )

        if not opts.join:
            plotter.plot_all(spgp.SPGBasePlotter)
        else:
            plotter.plot_all_join_outputs(spgp.SPGBasePlotter)
