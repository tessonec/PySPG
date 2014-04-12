'''
Created on Aug 29, 2011

@author: tessonec
'''


'''
Created on 12 Apr 2014

@author: tessonec
'''

import pandas as pd
import numpy as np

import matplotlib.pylab as plt
import matplotlib.lines as mlines


import matplotlib as mpl
import matplotlib.backends.backend_pdf as mpl_b_pdf
import itertools

class SPGPlotter:
    
    colors = ['black','blue', 'green', 'red', 'yellow', 'brown', 'grey', 'violet']
    markers  = mlines.Line2D.filled_markers
    #markers = [r'$\bigcirc$',r'$\bigtriangleup$',r'$\bigtriangledown$',r'$\diamondsuit$',r'$\maltese$',r'$\star$'] 

    font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 22,
        }

       
    axis_font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 22,
        }

    

    def __init__(self, table_name):
        
        
        mpl.rcParams['lines.linewidth'] = 2
        mpl.rcParams['font.family'] = 'serif'
        mpl.rcParams['font.serif'] = 'Times, Palatino, New Century Schoolbook, Bookman, Computer Modern Roman'
        mpl.rcParams['font.sans-serif'] = 'Helvetica, Avant Garde, Computer Modern Sans serif'
        mpl.rcParams['font.cursive'] = 'Zapf Chancery'
        mpl.rcParams['font.monospace'] = 'Courier, Computer Modern Typewriter'
        mpl.rcParams['text.usetex'] = 'true'
        # mpl.rcParams['text.latex', preamble=r'\usepackage{cmbright}')
        self.column_names = open(table_name).readline().split() # column_names
        
        self.df = pd.DataFrame( 
                np.loadtxt(table_name, skiprows =1 ),  
                columns = self.column_names
            )
        self.color_wheel = 0
        self.symbol_wheel = 0



    def get_transformed_var(self, var):
        if var in self.dict_of_vars:
            return self.dict_of_vars[var].replace("$","")
        else:
            return var.replace("$","").replace("_","\_")



    def add_curves(self, local_df, local_gr, curr_y_axis):
        
        
        
        df_coalesced = local_df.groupby(self.coalesced_vars)
        
        color_it = itertools.cycle(self.colors) 
        marker_it =  itertools.cycle(self.markers)
        for minimal_gr in sorted( df_coalesced.groups ):
            
            minimal_idx = df_coalesced.groups[minimal_gr]
            
            minimal_df = self.df.ix[ minimal_idx ]
             
            if type(minimal_gr) != type( (0,) ):
                minimal_gr = [minimal_gr]
            minimal_legend = ", ".join( [ 
                                         "$%s = %s$"%(self.get_transformed_var(k),v) 
                                         for (k,v) in zip(self.coalesced_vars, minimal_gr)
                                         ] )
#            print local_legend,  "------>",minimal_legend

            plt.scatter(  
                                    minimal_df[[self.x_axis]], minimal_df[[curr_y_axis]] , 
                                    label = minimal_legend, marker = marker_it.next(), color = color_it.next(), edgecolors = "black", s = 65)
            
            
            
        

    def plot_all(self, output_name):
        df_separated = self.df.groupby(self.separated_vars, sort = True)
        pp = mpl_b_pdf.PdfPages( output_name )
        
        for local_gr in  sorted( df_separated.groups):
            local_idx = df_separated.groups[local_gr]
            
            local_df = self.df.ix[ local_idx ]
            
            # sets-up title
            if type(local_gr) != type((0,)):
                local_gr = [local_gr]
            local_title = ", ".join( [ 
                                   "$%s = %s$"%(self.get_transformed_var(k),v) 
                                   for (k,v) in zip(self.separated_vars, local_gr)
                                  ] )
            print local_title, 
            for curr_y_axis in self.y_axis:
                print curr_y_axis, 
                # creates figure
                curr_fig = plt.figure()
                # adds all curves
                self.add_curves( local_df, local_gr, curr_y_axis )
                plt.legend()
                
                # sets-up title
                plt.title(local_title)         
                
                # sets-up axes
                plt.xlabel("$%s$"%self.get_transformed_var(self.x_axis), self.axis_font)
                
                plt.ylabel("$%s$"%self.get_transformed_var(curr_y_axis), self.axis_font)
                
                
                
                curr_axes =plt.gca()
                curr_axes.tick_params( labelsize = 18 )
                
                 
                if self.dict_of_settings.has_key(curr_y_axis):
                    if self.dict_of_settings[curr_y_axis].has_key('ylim'):
                        plt.ylim(self.dict_of_settings[curr_y_axis]['ylim'])
                    if self.dict_of_settings[curr_y_axis].has_key('yscale'):
                        curr_axes.set_yscale(self.dict_of_settings[self.y_axis]['yscale'])
                if self.dict_of_settings.has_key(self.x_axis):
                    if self.dict_of_settings[self.x_axis].has_key('xlim'):
                        plt.xlim(self.dict_of_settings[self.x_axis]['xlim'])
                    if self.dict_of_settings[self.x_axis].has_key('xscale'):
                        curr_axes.set_xscale(self.dict_of_settings[self.x_axis]['xscale'])
                plt.savefig(pp, format='pdf')
            print         
            
        pp.close()








class SPGSubPlotter(SPGPlotter):


    def plot_all(self, output_name):
        df_separated = self.df.groupby(self.separated_vars, sort = True)
        pp = mpl_b_pdf.PdfPages( output_name )
        
        for curr_page in self.y_axis:
            for local_gr in  sorted( df_separated.groups):
                local_idx = df_separated.groups[local_gr]
            
                local_df = self.df.ix[ local_idx ]
            
            # sets-up title
                if type(local_gr) != type((0,)):
                    local_gr = [local_gr]
                local_title = ", ".join( [ 
                                   "$%s = %s$"%(self.get_transformed_var(k),v) 
                                   for (k,v) in zip(self.separated_vars, local_gr)
                                  ] )
                print local_title, curr_page
                for irow, curr_y_axis in enumerate(curr_page):   
                     
                # creates figure
                    curr_fig = plt.subplot(len(curr_page), 1, irow)
                # adds all curves
                    self.add_curves( local_df, local_gr, curr_y_axis )
                    plt.legend()
                
                # sets-up title
                    plt.title(local_title)         
                
                # sets-up axes
                    plt.xlabel("$%s$"%self.get_transformed_var(self.x_axis), self.axis_font)
                
                    plt.ylabel("$%s$"%self.get_transformed_var(curr_y_axis), self.axis_font)
                
                 
                 
                    curr_axes =plt.gca()
                    curr_axes.tick_params( labelsize = 18 )
                
                 
                    if self.dict_of_settings.has_key(curr_y_axis):
                        if self.dict_of_settings[curr_y_axis].has_key('ylim'):
                            plt.ylim(self.dict_of_settings[curr_y_axis]['ylim'])
                        if self.dict_of_settings[curr_y_axis].has_key('yscale'):
                            curr_axes.set_yscale(self.dict_of_settings[self.y_axis]['yscale'])
                    if self.dict_of_settings.has_key(self.x_axis):
                        if self.dict_of_settings[self.x_axis].has_key('xlim'):
                            plt.xlim(self.dict_of_settings[self.x_axis]['xlim'])
                        if self.dict_of_settings[self.x_axis].has_key('xscale'):
                            curr_axes.set_xscale(self.dict_of_settings[self.x_axis]['xscale'])
                    plt.savefig(pp, format='pdf')
                         
            
        pp.close()








