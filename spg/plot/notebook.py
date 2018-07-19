#!/usr/bin/python
'''
Created on 12 Apr 2014

@author: tessonec
'''

import spg.plot as spgp
import spg.base as spgb 
import spg.utils as spgu


import pandas as pd
import numpy as np
import math as m



import os.path
import re

import ipywidgets as ipyw
import itertools

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as mpll

from IPython.display import display



from spg import CONFIG_DIR

# from spg.utils import newline_msg, evaluate_string, load_configuration

from spg.plot import DataFrameIterator

class BaseDataLoader:


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

    #
    # def setup_coalesced_vars(self, cv):
    #     all_vars = self.separated_vars + self.coalesced_vars
    #     for v in cv:
    #         if v in all_vars or v == self.independent_var:
    #             all_vars.remove(v)
    #     self.coalesced_vars = cv
    #     self.separated_vars = all_vars
    #
    #
    # def setup_separated_vars(self, sv):
    #     all_vars = self.separated_vars + self.coalesced_vars
    #     for v in sv:
    #         if v in all_vars or v == self.independent_var:
    #             all_vars.remove(v)
    #     self.coalesced_vars = all_vars
    #     self.separated_vars = sv
    #
    # def setup_independent_var(self, v):
    #     if v in self.coalesced_vars:
    #         self.coalesced_vars.remove(v)
    #         self.independent_var = v
    #     if v in self.separated_vars:
    #         self.separated_vars.remove(v)
    #         self.independent_var = v


    # def cycle_all(self, f_local):
    #
    #     ret = []
    #     for outer_df in DataFrameIterator( self.data, self.separated_vars ):
    #         for inner_df in DataFrameIterator( outer_df, self.coalesced_vars ):
    #
    #             r_loc = f_local(outer_df, inner_df )
    #             ret.append(r_loc)
    #     return ret

    def get_separated_values(self):

        ret = []
        for outer_df in DataFrameIterator(self.data, self.separated_vars):
            ret.append( [ outer_df[v].unique()[0] for v in self.separated_vars ] )
        return ret

    def get_coalesced_values(self):

        ret = []
        for inner_df in DataFrameIterator(self.data, self.coalesced_vars):
            ret.append( [ inner_df[v].unique()[0] for v in self.coalesced_vars ] )

        return ret


    #
    # def outer_inner(self, outer_df, inner_df):
    #     ouv = [ outer_df[v].unique()[0] for v in self.separated_vars ]
    #     iuv = [ inner_df[v].unique()[0] for v in self.coalesced_vars ]
    #
    #     return ouv, iuv


class CSVDataLoader(BaseDataLoader):
    def __init__(self, ds_filename, output_columns=[], settings={}):
        self.full_dataframe = pd.read_csv(ds_filename)

        self.output_columns = output_columns

        self.constants = {}
        self.variables = []
        for vn in self.full_dataframe.keys():
            if vn in self.output_columns:
                continue
            all_values = self.full_dataframe[vn].unique()
            if len(all_values) > 1:
                self.variables.append(vn)
            else:
                self.constants[vn] = self.full_dataframe[vn].unique()[0]

        self.independent_var = self.variables[-1]

        try:
            self.coalesced_vars = [self.variables[-2]]
        except:
            self.coalesced_vars = []
        try:
            self.separated_vars = self.variables[:-2]
        except:
            self.separated_vars = []

        self.data = self.full_dataframe[self.variables + self.output_columns]

        self.settings = settings


        print "[__init__] constants: %s"% self.constants.keys()
        print "[__init__] independent variables: %s"% self.variables
        print "[__init__] output columns: %s"% self.output_columns


    def configure_vars(self, separated_vars, coalesced_vars, independent_var=None, recalculate_output_columns=True):
        all_vars = separated_vars + coalesced_vars
        if independent_var is not None:
            all_vars.append(independent_var)

        # No unknown columns are present
        assert len(set(all_vars) - set(self.data)) == 0
        # All sets are disjoint
        assert independent_var not in separated_vars
        assert independent_var not in coalesced_vars
        assert len(set(separated_vars).intersection(coalesced_vars)) == 0

        self.separated_vars = separated_vars
        self.coalesced_vars = coalesced_vars
        self.independent_var = independent_var

        self.variables = all_vars

#        print self.variables
        if recalculate_output_columns:
            self.output_columns = [kn for kn in self.data.keys() if kn not in self.variables]



class SPGDataLoader(BaseDataLoader):
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

        self.full_dataframe = pd.read_csv(self.datafile_name)

        settings_output, self.output_columns = spgu.load_configuration(
            "%s.stdout" % self.simulation.command.split(".")[0])


        self.constants = {}
        self.variables = []
        for vn in self.full_dataframe.keys():
            if vn in self.output_columns:
                continue
            all_values = self.full_dataframe[vn].unique()
            if len(all_values) > 1:
                self.variables.append(vn)
            else:
                self.constants[vn] = self.full_dataframe[vn].unique()[0]

#        print spgu.load_configuration( "%s.input" % self.simulation.command.split(".")[0])


        try:
            self.settings, foo =  spgu.load_configuration( "%s.input" % self.simulation.command.split(".")[0])
        except:
            self.settings = spgu.SPGSettings()
            spgu.newline_msg( "INF", "no 'input' file found: %s"%self.simulation.command)
        self.settings.update(settings_output)
        try:
            self.coalesced_vars = [self.variables[-2]]
        except:
            self.coalesced_vars = []

        try:
            self.separated_vars = self.variables[:-2]
        except:
            self.separated_vars = []

        self.independent_var = self.variables[-1]

        x_axis_iter = self.simulation.data[ self.simulation.position_of(self.independent_var)]
        if not self.settings.has_key( self.independent_var ):
            self.settings[ self.independent_var ] = spgu.SPGSettings()
        if x_axis_iter.type == "*":
            self.settings[self.independent_var]['scale'] = 'log'
            self.settings[self.independent_var]['lim'] =  (x_axis_iter.xmin, x_axis_iter.xmax)



        self.data = self.full_dataframe[self.variables + self.output_columns]

        print "[__init__] constants: %s"% self.constants.keys()
        print "[__init__] independent variables:", self.separated_vars, self.coalesced_vars, self.independent_var
        print "[__init__] output columns: %s"% self.output_columns


    def configure_vars(self, separated_vars, coalesced_vars, independent_var = None):

        all_vars = separated_vars + coalesced_vars
        if independent_var is not None:
            all_vars.append( independent_var )

        # No unknown columns are present
        try:
            assert len(set(all_vars) - set(self.data.keys() )) == 0
        except:
            print "[configure_vars] ", set(all_vars) - set(self.data.keys() ), "not recognised as column name"
            return
        # All sets are disjoint
        try:
            assert independent_var not in separated_vars
        except:
            print "[configure_vars] ", independent_var, "is alse in separated_vars"
            return

        try:
            assert independent_var not in coalesced_vars
        except:
            print "[configure_vars] ", independent_var, "is alse in coalesced_vars"
            return

        assert len(set(separated_vars).intersection(coalesced_vars)) == 0
        # No output column is used
        assert len(set(all_vars).intersection(self.output_columns)) == 0

        self.separated_vars = separated_vars
        self.coalesced_vars = coalesced_vars
        self.independent_var = independent_var

        self.variables = all_vars

#        self.output_columns = [kn for kn in self.data.keys() if kn not in self.variables]

        #self.__initialise_independent_elements()


#########################################################################################
#########################################################################################
class SPGInteractivePlotter:

        colors = ['black', 'blue', 'green', 'red', 'yellow', 'brown', 'grey', 'violet']
        markers = mpll.Line2D.filled_markers

        def __init__(self, splotter, xscale = 'linear', yscale = 'linear'):
            # self.splotter = splotter

            self.full_data = splotter.data

            self.separated_vars = splotter.separated_vars
            self.separated_values = splotter.get_separated_values()
            self.separated_selection = self.separated_values[0]

            self.coalesced_vars = splotter.coalesced_vars
            self.coalesced_values = splotter.get_coalesced_values()


            self.output_columns = splotter.output_columns
            self.dependent_var = self.output_columns[0]

            self.independent_var = splotter.independent_var
            self.figure, self.axis = plt.subplots(1, 1, figsize=(12, 6))

            self.settings = splotter.settings

            if len(self.separated_vars) == 0:
                vec_labels = ["all values"]
            else:
                vec_labels = [(", ".join(map(str, ou)), ou) for ou in self.separated_values]
#            print vec_labels
            self.dd_filter = ipyw.Dropdown(
                options=vec_labels)  # ,
            # description = "%s :"%(self.separated_vars) )
            self.dd_output = ipyw.Dropdown(
                options=self.output_columns)  # ,

            self.select_xscale = ipyw.Checkbox(
                value= xscale == "log",
                description='x log scale',
                icon='check'
            )

            self.select_yscale = ipyw.Checkbox(
                value= yscale == "log",
                description='y log scale',
                icon='check'
            )

            # description = "Output columns: ")

            self.xscale = xscale
            self.yscale = yscale

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
            #print query_str
            if len(query_str) > 0:
                self.data = self.full_data.query(query_str)
            else:
                self.data = self.full_data

        def on_select_scale(self, change):

            mpl.rcParams['text.usetex'] = 'false'
            #     if not change.has_key('new'): return
            if change['owner'] == self.select_xscale:
                self.xscale = "log" if change['new'] else "linear"
                #print xscale
                self.axis.set_xscale(self.xscale)
            if change['owner'] == self.select_yscale:
                self.yscale = "log" if change['new'] else "linear"
                self.axis.set_yscale(self.yscale)
            self.__recalculate_lims()
            self.axis.figure.canvas.draw()

        def on_dd_filter_value_change(self, change):
            self.separated_values = change['new']
            self.__separated_value_change()
            self.redraw()

        def on_dd_output_value_change(self, change):
            self.dependent_var = change['new']

            self.redraw()

        def redraw(self):


            mpl.rcParams['text.usetex'] = 'false'
            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)

            for ix, iv in enumerate(self.coalesced_values):
                query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
                if len(query_inn_str) > 0:
                    local_df = self.data.query(query_inn_str)
                else:
                    local_df = self.data

                self.axis.lines[ix].set_data(local_df[self.independent_var], local_df[self.dependent_var])

            self.axis.set_xlabel(self.independent_var)
            self.axis.set_ylabel(self.dependent_var)
            self.__recalculate_lims()


            self.axis.figure.canvas.draw()

        def draw(self):

            mpl.rcParams['text.usetex'] = 'false'
            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)
            for iv in self.coalesced_values:
                query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])

                if len(query_inn_str) > 0:
                    local_df = self.data.query(query_inn_str)
                else:
                    local_df = self.data
#                print query_inn_str
                self.axis.plot(local_df[self.independent_var], local_df[self.dependent_var],
                               linestyle='', marker=marker_it.next(), color=color_it.next(),
                               label=query_inn_str)

#            self.axis.set_ylim(min(self.data[self.dependent_var]), max(self.data[self.dependent_var]))
#            self.axis.set_xlim(min(self.data[self.independent_var]), max(self.data[self.independent_var]))
            self.axis.set_xlabel(self.independent_var)
            self.axis.set_ylabel(self.dependent_var)

            box = self.axis.get_position()
            self.axis.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            self.axis.legend(loc='upper right' ) #, bbox_to_anchor=(1, 0.5))

            self.__recalculate_lims()

            self.axis.figure.canvas.draw()

        def savefig(self, filename, draw_legend = True):
            mpl_rcParams = mpl.rcParams.copy()

            spgp.init_mpl()
            mpl.rcParams['text.usetex'] = 'True'

            fig_out, axis_out = plt.subplots(1, 1, figsize=(8, 4))

            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)
            for iv in self.coalesced_values:
                query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
                if len(query_inn_str) > 0:
                    local_df = self.data.query(query_inn_str)
                else:
                    local_df = self.data
                label_str = ", ".join(["%s=%s" % i for i in zip(self.coalesced_vars, iv)])
                axis_out.plot(local_df[self.independent_var], local_df[self.dependent_var],
                               linestyle='', marker=marker_it.next(), color=color_it.next(),
                               label=label_str.replace("_", " "))
           #     print label_str

            self.__recalculate_lims(axis_out)
            axis_out.tick_params()

            if self.settings[self.independent_var].has_key("label"):
                xlabel = self.settings[self.independent_var]["label"]
            else:
                xlabel = self.independent_var.replace("_"," ")

            if self.settings[self.dependent_var].has_key("label"):
                ylabel = self.settings[self.dependent_var]["label"]
            else:
                ylabel = self.dependent_var.replace("_"," ")

            # print xlabel, ylabel

            axis_out.set_xlabel(xlabel)
            axis_out.set_ylabel(ylabel)


            axis_out.set_xscale(self.xscale)
            axis_out.set_yscale(self.yscale)

        ###    axis_out.set_title(
        ###        ", ".join([" %s=%s".replace("_", " ") % i for i in zip(self.separated_vars, self.separated_values)]),
        ###        axis_font)
            title = ", ".join([" %s=%s" % i for i in zip(self.separated_vars, self.separated_values)])
            title = title.replace("_", " ")

            axis_out.set_title(title)

            box = axis_out.get_position()
            axis_out.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            if draw_legend:
                axis_out.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            axis_out.figure.canvas.draw()
            fig_out.savefig(filename, bbox_inches='tight',
                            transparent=True,
                            pad_inches=0)

            mpl.rcParams = mpl_rcParams

        def __recalculate_lims(self, axis_out = None):
            ydata = self.data[self.dependent_var]
            xdata = self.data[self.independent_var]
            if self.select_yscale.value:  # it is not log
                ydata = ydata[ydata > 1e-9]

#            print ydata

            ymin, ymax = 0.9*np.min(ydata), 1.1*np.max(ydata)
            if self.select_xscale.value:  # it is not log
                xdata = xdata[xdata > 1e-9]
            xmin, xmax = 0.9*np.min(xdata), 1.1*np.max(xdata)

            self.axis.set_xscale(self.xscale)
            self.axis.set_yscale(self.yscale)

            if axis_out:
                axis_out.set_ylim(ymin, ymax)
                axis_out.set_xlim(xmin, xmax)

            else:

                self.axis.set_ylim(ymin, ymax)
                self.axis.set_xlim(xmin, xmax)


#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################



class SPGInteractiveScalingPlotter:
    colors = ['black', 'blue', 'green', 'red', 'yellow', 'brown', 'grey', 'violet']
    markers = mpll.Line2D.filled_markers

    def __init__(self, splotter):
        self.full_data = splotter.data

        self.separated_values = splotter.get_separated_values()
        self.separated_vars = splotter.separated_vars
        self.separated_selection = self.separated_values[0]

        self.coalesced_values = splotter.get_coalesced_values()
        self.coalesced_vars = splotter.coalesced_vars

        self.output_columns = splotter.output_columns
        self.dependent_var = self.output_columns[0]

        self.independent_var = splotter.independent_var

        self.constants = splotter.constants
        self.variables = [ i for i in self.full_data.keys() if not self.constants.has_key( i ) ]

        self.settings = splotter.settings

        if len(self.separated_vars) == 0:
            vec_labels = ["all values"]
        else:
            vec_labels = [(", ".join(map(str, ou)), ou) for ou in self.separated_values]

        self.dd_filter = ipyw.Dropdown(
            options=vec_labels)

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

        self.select_yscale.observe(self.on_select_scale, names=['value', 'owner'])
        self.select_xscale.observe(self.on_select_scale, names=['value', 'owner'])

        self.__separated_value_change()
        self.__scaling_parameters = {}
        self.scaling_values = {}
        self.__scaling_widgets = {}
        self.xscale = "linear"
        self.yscale = "linear"

    def interact(self):

        vec_row2 = []
        for sp in sorted(self.__scaling_parameters.keys()):
            (value, value_min, value_max, step) = self.__scaling_parameters[sp]
            vec_row2.append(ipyw.Label("%s: " % (sp)))
            new_slider = ipyw.FloatSlider(value=value, min=value_min, max=value_max, step=step)

            vec_row2.append(new_slider)
            self.__scaling_widgets[new_slider] = sp
            new_slider.observe(self.on_slider_change, names=['value'])

        display(
            ipyw.VBox([
                ipyw.HBox([ipyw.Label("%s: " % (self.separated_vars)), self.dd_filter, self.select_xscale,
                           self.select_yscale]),
                ipyw.HBox(vec_row2)
            ])
        )

        self.figure, self.axis = plt.subplots(1, 1, figsize=(8, 4))

        self.transform_data()
        self.draw()

    def __separated_value_change(self):

        query_str = " & ".join(["(%s==%s)" % i for i in zip(self.separated_vars, self.separated_values)])
        if len(query_str) > 0:
            self.data = self.full_data.query(query_str)
        else:
            self.data = self.full_data.copy()


        self.data = self.data[ sorted( set(self.variables + self.output_columns) )]



    def on_slider_change(self, change):
        par_name = self.__scaling_widgets[change['owner']]
        self.scaling_values[par_name] = change['new']
        self.transform_data()

        # print self.scaling_values, self.evaluate_string(self.x_transform), self.evaluate_string(self.y_transform)
        self.redraw()

    def on_select_scale(self, change):

        if change['owner'] == self.select_xscale:
            self.xscale = "log" if change['new'] else "linear"

            self.axis.set_xscale(self.xscale)
        if change['owner'] == self.select_yscale:
            self.yscale = "log" if change['new'] else "linear"
            self.axis.set_yscale(self.yscale)

        self.axis.figure.canvas.draw()

    def on_dd_filter_value_change(self, change):

        self.separated_values = change['new']
        self.__separated_value_change()
        self.redraw()

    def evaluate_string(self, to_evaluate):
        res = to_evaluate
        for i_var in self.constants:
            res = re.sub(r'\{%s\}' % i_var, str(self.constants[i_var]), res)

        for i_var in self.scaling_values:
            res = re.sub(r'\{%s\}' % i_var, str(self.scaling_values[i_var]), res)

        for i_var in self.variables:
            res = re.sub(r'\{%s\}' % i_var, "self.data['%s']" % i_var, res)



        return eval(res)

    def setup_transforms(self, xt, yt):
        rx = re.compile(r'\{([a-zA-Z0-9_]\w*)\}')
        vars_in_x_expr = rx.findall(xt)
        vars_in_y_expr = rx.findall(yt)
        possible_keys = self.constants.keys() + self.variables + self.output_columns + self.__scaling_parameters.keys()
#        print possible_keys

        assert len(set(vars_in_x_expr) - set(possible_keys)) == 0
        assert len(set(vars_in_y_expr) - set(possible_keys)) == 0

        self.x_transform = xt
        self.y_transform = yt

    def add_scaling_parameter(self, parameter_name, value, value_min=0., value_max=None, step=0.01):
        if value_max is None:
            value_max = 2. * value

        self.__scaling_parameters[parameter_name] = (value, value_min, value_max, step)
        self.scaling_values[parameter_name] = value

    def transform_data(self):
        self.data_transformed = self.data.copy()
#        print self.x_transform, self.y_transform

        self.data_transformed['transformed_x'] = self.evaluate_string(self.x_transform)
        self.data_transformed['transformed_y'] = self.evaluate_string(self.y_transform)

    def redraw(self):
        color_it = itertools.cycle(self.colors)
        marker_it = itertools.cycle(self.markers)

        for ix, iv in enumerate(self.coalesced_values):
            query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
            if len(query_inn_str) > 0:
                local_df = self.data_transformed.query(query_inn_str)
            else:
                local_df = self.data_transformed

            self.axis.lines[ix].set_data(local_df['transformed_x'], local_df['transformed_y'])

        self.__recalculate_lims()

        self.axis.figure.canvas.draw()

    def draw(self):

        color_it = itertools.cycle(self.colors)
        marker_it = itertools.cycle(self.markers)
        for iv in self.coalesced_values:
            query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
            if len(query_inn_str) > 0:
                local_df = self.data_transformed.query(query_inn_str)
            else:
                local_df = self.data_transformed
            self.axis.plot(local_df['transformed_x'], local_df['transformed_y'],
                           linestyle='', marker=marker_it.next(), color=color_it.next(),
                           label=query_inn_str)

        self.__recalculate_lims()
        self.axis.set_xlabel('transformed_x')
        self.axis.set_ylabel('transformed_y')

        box = self.axis.get_position()
        self.axis.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        self.axis.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        self.axis.figure.canvas.draw()


    def savefig(self, filename, xlabel, ylabel, draw_legend = True):

#        spgp.init_mpl()

        fig_out, axis_out = plt.subplots(1, 1, figsize=(12, 6))

        color_it = itertools.cycle(self.colors)
        marker_it = itertools.cycle(self.markers)
        for iv in self.coalesced_values:
            query_inn_str = " & ".join(["(%s==%s)" % i for i in zip(self.coalesced_vars, iv)])
            if len(query_inn_str) > 0:
                local_df = self.data_transformed.query(query_inn_str)
            else:
                local_df = self.data_transformed

            label_str = ", ".join(["%s=%s" % i for i in zip(self.coalesced_vars, iv)])
            axis_out.plot(local_df['transformed_x'], local_df['transformed_y'],
                           linestyle='', marker=marker_it.next(), color=color_it.next(),
                           label=label_str.replace("_"," "))

        self.__recalculate_lims(axis_out)
#        axis_out.tick_params(labelsize=axis_font["size"] - 6)

        axis_out.set_xlabel(xlabel)
        axis_out.set_ylabel(ylabel)

        axis_out.set_xscale(self.xscale)
        axis_out.set_yscale(self.yscale)
        title = ", ".join([" %s=%s" % i for i in zip(self.separated_vars, self.separated_values)])
        title = title.replace("_", " ")

        axis_out.set_title(title)

        box = axis_out.get_position()
        axis_out.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        if draw_legend:
            axis_out.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        axis_out.figure.canvas.draw()
        fig_out.savefig( filename,  bbox_inches='tight',
               transparent=True,
               pad_inches=0 )


    def __recalculate_lims(self, axis_out = None):
        ydata = self.data_transformed['transformed_y']
        xdata = self.data_transformed['transformed_x']
        if self.select_yscale.value:  # it is not log
            ydata = ydata[ydata > 0]
        ymin, ymax = 0.9 * min(ydata), 1.1 * max(ydata)
        if self.select_xscale.value:  # it is not log
            xdata = xdata[xdata > 0]
        xmin, xmax = 0.9 * min(xdata), 1.1 * max(xdata)

        if axis_out:
            axis_out.set_ylim(ymin, ymax)
            axis_out.set_xlim(xmin, xmax)

        else:

            self.axis.set_ylim(ymin, ymax)
            self.axis.set_xlim(xmin, xmax)

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
# def parse_command_line():
#      from optparse import OptionParser
#
#      parser = OptionParser()
#
#      parser.add_option("--coalesced", type="string", action='store', dest="coalesced",
# 		        default = [],
#                         help = "comma separated list of coalesced variables")
#
#      parser.add_option("--separated", type="string", action='store', dest="separated",
# 		        default = [],
#                         help = "comma separated list of separated variables")
#
#      parser.add_option("--output", type="string", action='store', dest="output",
#                        default=[],
#                        help="output structure")
#
#      parser.add_option("--join", action='store_true', dest="join",
#                        default=[],
#                        help="join all y columns")
#
#      opts, args = parser.parse_args()
#      if len( opts.coalesced ) >0:
#          opts.coalesced = opts.coalesced.split(",")
#      if len( opts.separated ) >0:
#          opts.separated = opts.separated.split(",")
#      if len( opts.output ) >0:
#          opts.output = opts.output.split(",")
#      return  opts, args


#
#
#
# if __name__ == "__main__":
#     opts, args = parse_command_line()
#
#     for iarg in args:
#
#         plotter = SPGDataLoader(iarg)
#         if len(opts.coalesced) > 0:
#             plotter.setup_coalesced_vars( opts.coalesced )
#         if len(opts.separated) > 0:
#             plotter.setup_separated_vars( opts.separated )
#         if len(opts.output) > 0:
#             plotter.setup_output_columns( opts.output )
#
#         if not opts.join:
#             plotter.plot_all(spgp.SPGBasePlotter)
#         else:
#             plotter.plot_all_join_outputs(spgp.SPGBasePlotter)
