import pandas as pd
import pandas.io.parsers as pdp

import numpy as np

import math as m
import datetime as dt

import matplotlib as mpl
import matplotlib.backends.backend_pdf as mpl_b_pdf
import matplotlib.lines as mlines
import matplotlib.pyplot as plt


import matplotlib.dates as mdates
import matplotlib.ticker as pltt

import itertools

import datetime as dt


def get_available_fonts(dir_name=None):
    """
    returns the list of fonts already installed in the system
    """
    if dir_name is not None:
        font_list = [f.name for f in mpl.font_manager.createFontList(mpl.font_manager.findSystemFonts(dir_name))]
    else:
        font_list = [f.name for f in mpl.font_manager.createFontList(mpl.font_manager.findSystemFonts())]

    return sorted(set(font_list))


def init_mpl(usetex=True, font="CMU Sans Serif"):
    """
    possible fonts are 'CMU Sans Serif', 'Gill Sans', 'Helvetica Neue', 'Neutraface Text'
    """

    mpl.rcParams['text.usetex'] = usetex

    if font.lower().find("sans") != -1:
         mpl.rcParams['text.latex.preamble'] = [r'\usepackage[cm]{sfmath}']

    if usetex:
        mpl.rcParams['text.latex.preamble'] = [r'\usepackage[cm]{sfmath}']
    else:
        mpl.rcParams['font.sans-serif'] = font
        mpl.rcParams['font.family'] = "sans-serif"

    mpl.rcParams['lines.linewidth'] = 2.5
    mpl.rcParams['lines.markersize'] = 10
    mpl.rcParams['lines.markeredgewidth'] = 2.5

    mpl.rcParams['axes.linewidth'] = 2

    mpl.rcParams['axes.labelsize'] = 24
    mpl.rcParams['legend.fontsize'] = 20
    mpl.rcParams['xtick.labelsize'] = 18
    mpl.rcParams['ytick.labelsize'] = 18

    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams['xtick.bottom'] = True
    mpl.rcParams['xtick.major.size'] = 6
    mpl.rcParams['xtick.minor.size'] = 4
    mpl.rcParams['xtick.major.width'] = 1.5
    mpl.rcParams['xtick.minor.width'] = 1

    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['ytick.left'] = True
    mpl.rcParams['ytick.right'] = True
    mpl.rcParams['ytick.major.size'] = 6
    mpl.rcParams['ytick.minor.size'] = 4
    mpl.rcParams['ytick.major.width'] = 1.5
    mpl.rcParams['ytick.minor.width'] = 1


class SPGBasePlotter:

    colors = ['orange' ,'blue', 'green', 'red', 'yellow', 'brown', 'grey', 'violet']
    markers  = mlines.Line2D.filled_markers

    # markers = [r'$\bigcirc$',r'$\bigtriangleup$',r'$\bigtriangledown$',r'$\diamondsuit$',r'$\maltese$',r'$\star$']


    def __init__(self, table_name, figsize = (9,6)):
        mpl.rcParams['figure.figsize'] = figsize

        init_mpl()


        # mpl.rcParams['text.latex', preamble=r'\usepackage{cmbright}')
        self.column_names = open(table_name).readline().split() # column_names

        self.df = pd.read_csv(table_name)




    def get_transformed_var(self, var, keep_tex = False):
        if isinstance(var, type((0,))):
            var, foo = var
        if not keep_tex:
            if var in self.settings and "label" in self.settings[var]:
#            return self.settings[var]["label"].replace("\\\\", '\\')

                return self.settings[var]["label"].replace("$" ,"").replace("\\\\" ,'\\')

            else:
                return var.replace("$" ,"").replace("_" ,"\_")
        else:
            if var in self.settings and "label" in self.settings[var]:
                return self.settings[var]["label"].replace("\\\\", '\\')

            else:
                return var.replace("_", "\_")

    def add_curves(self, local_df, curr_y_axis, subp, legend_prepend = ""):
        if len(self.coalesced_vars) > 0:
            df_coalesced = local_df.groupby(self.coalesced_vars)
            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)
            for minimal_gr in sorted(df_coalesced.groups):

                minimal_idx = df_coalesced.groups[minimal_gr]

                minimal_df = self.df.ix[minimal_idx]

                if not isinstance(minimal_gr, type((0,))):
                    minimal_gr = [minimal_gr]
                minimal_legend = legend_prepend + ", ".join([
                                                                "$%s = %s$" % (self.get_transformed_var(k), v)
                                                                for (k, v) in zip(self.coalesced_vars, minimal_gr)
                                                                ])
                #print "------>",minimal_legend
                if isinstance(curr_y_axis, type("")):
                    subp.scatter(minimal_df[[self.x_axis]], minimal_df[[curr_y_axis]],
                                 label=minimal_legend, marker=next(marker_it), color=next(color_it),
                                 edgecolors="black", s=65)
                elif isinstance(curr_y_axis, type((0,))) and len(curr_y_axis) == 2:
                    ## BROKEN
                    curr_y_axis, curr_yerr = curr_y_axis
                    ####### B
                    # subp.errorbar( x=minimal_df[[self.x_axis]], y=minimal_df[[curr_y_axis]] ,yerr = minimal_df[[curr_yerr]],
                    #           label = minimal_legend, fmt = marker_it.next(), color = color_it.next(), edgecolors = "black", s = 65 )
                    subp.errorbar(x=minimal_df[[self.x_axis]].apply(np.float32),
                                  y=minimal_df[[curr_y_axis]].apply(np.float32),
                                  yerr=minimal_df[[curr_yerr]].apply(np.float32))


        else:
            color_it = itertools.cycle(self.colors)
            marker_it = itertools.cycle(self.markers)

            minimal_legend = legend_prepend

            if isinstance(curr_y_axis, type("")):
                subp.scatter(local_df[[self.x_axis]], local_df[[curr_y_axis]],
                             label=minimal_legend, marker=next(marker_it), color=next(color_it),
                             edgecolors="black", s=65)
            elif isinstance(curr_y_axis, type((0,))) and len(curr_y_axis) == 2:
                ## BROKEN
                curr_y_axis, curr_yerr = curr_y_axis
                ####### B
                # subp.errorbar( x=minimal_df[[self.x_axis]], y=minimal_df[[curr_y_axis]] ,yerr = minimal_df[[curr_yerr]],
                #           label = minimal_legend, fmt = marker_it.next(), color = color_it.next(), edgecolors = "black", s = 65 )
                subp.errorbar(x=local_df[[self.x_axis]].apply(np.float32),
                              y=local_df[[curr_y_axis]].apply(np.float32),
                              yerr=local_df[[curr_yerr]].apply(np.float32))

    def plot_all(self, output_name):
        pp = mpl_b_pdf.PdfPages(output_name)

        if len(self.separated_vars) == 0:
            df_separated = self.df

            for curr_y_axis in self.y_axis:
                # print curr_y_axis,
                # creates figure
                #curr_fig = plt.figure(figsize=FIGSIZE)
                plt.clf()

                # adds all curves
                self.add_curves(df_separated, curr_y_axis, plt.gca())
                plt.legend()

                # sets-up title
                #        plt.title(local_title)

                # sets-up axes
                plt.xlabel(self.get_transformed_var(self.x_axis, keep_tex=True))

                plt.ylabel(self.get_transformed_var(curr_y_axis, keep_tex=True))

                curr_axes = plt.gca()
                curr_axes.tick_params(labelsize=18)

                yaxis_lim_set = False
                yaxis_scale = "linear"

                if curr_y_axis in self.settings:
                    # print self.settings[curr_y_axis],
                    if 'lim' in self.settings[curr_y_axis]:
                        plt.ylim(self.settings[curr_y_axis]['lim'])
                        yaxis_lim_set = True
                    if 'scale' in self.settings[curr_y_axis]:
                        curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
                        yaxis_scale = self.settings[curr_y_axis]['scale']


                if not yaxis_lim_set:
                    yseries = df_separated[[curr_y_axis]]
                    if yaxis_scale == 'lin':
                        rng = yseries.max()-yseries.min()
                        yscale = yseries.min()-rng*0.05, yseries.max()+rng*0.05
                    else:
                        yscale = yseries[yseries > 0].min()*0.9, yseries[yseries > 0].max()*1.1

                    curr_axes.set_yscale(yscale)



                if self.x_axis in self.settings:
                    if 'lim' in self.settings[self.x_axis]:
                        plt.xlim(self.settings[self.x_axis]['lim'])
                    if 'scale' in self.settings[self.x_axis]:
                        curr_axes.set_xscale(self.settings[self.x_axis]['scale'])


                plt.tight_layout()
                plt.savefig(pp, format='pdf')
                plt.clf()




        else:
            df_separated = self.df.groupby(self.separated_vars, sort=True)

            for local_gr in sorted(df_separated.groups):
                local_idx = df_separated.groups[local_gr]

                local_df = self.df.ix[local_idx]

                # sets-up title
                if not isinstance(local_gr, type((0,))):
                    local_gr = [local_gr]
                local_title = ", ".join([
                                            "$%s = %s$" % (self.get_transformed_var(k), v)
                                            for (k, v) in zip(self.separated_vars, local_gr)
                                            ])
                # print local_title

                for curr_y_axis in self.y_axis:
                    # print curr_y_axis,
                    # creates figure
                    # curr_fig = plt.figure(figsize=FIGSIZE)
                    plt.clf()
                    # adds all curves
                    self.add_curves(local_df, curr_y_axis, plt.gca())
                                    #, legend_prepend=self.get_transformed_var(curr_y_axis))
                    plt.legend()

                    # sets-up title
                    plt.title(local_title)

                    # sets-up axes

                    plt.xlabel( self.get_transformed_var(self.x_axis, keep_tex=True))

                    plt.ylabel( self.get_transformed_var(curr_y_axis, keep_tex=True))

                    curr_axes = plt.gca()
                    curr_axes.tick_params(labelsize=18)

                    if curr_y_axis in self.settings:
                        # print self.settings[curr_y_axis],
                        if 'lim' in self.settings[curr_y_axis]:
                            plt.ylim(self.settings[curr_y_axis]['lim'])
                        if 'scale' in self.settings[curr_y_axis]:
                            curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
                    if self.x_axis in self.settings:
                        if 'lim' in self.settings[self.x_axis]:
                            plt.xlim(self.settings[self.x_axis]['lim'])
                        if 'scale' in self.settings[self.x_axis]:
                            curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                    plt.savefig(pp, format='pdf')
                    # print
                    plt.tight_layout()
                    plt.clf()

        pp.close()

    def plot_all_join_outputs(self, output_name):
        pp = mpl_b_pdf.PdfPages(output_name)

        if len(self.separated_vars) == 0:
            df_separated = self.df

            for curr_y_axis in self.y_axis:
                # print curr_y_axis,
                # creates figure
                #curr_fig = plt.figure(figsize=FIGSIZE)
                plt.clf()
                # adds all curves
                self.add_curves(df_separated, curr_y_axis, plt.gca())
                plt.legend()

                # sets-up title
                #        plt.title(local_title)

                # sets-up axes
                plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

            curr_axes = plt.gca()
            curr_axes.tick_params(labelsize=18)

            if curr_y_axis in self.settings:
                # print self.settings[curr_y_axis],
                if 'lim' in self.settings[curr_y_axis]:
                    plt.ylim(self.settings[curr_y_axis]['lim'])
                if 'scale' in self.settings[curr_y_axis]:
                    curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
            if self.x_axis in self.settings:
                if 'lim' in self.settings[self.x_axis]:
                    plt.xlim(self.settings[self.x_axis]['lim'])
                if 'scale' in self.settings[self.x_axis]:
                    curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
            plt.gca().tight_layout()
            plt.savefig(pp, format='pdf')




        else:
            df_separated = self.df.groupby(self.separated_vars, sort=True)

            for local_gr in sorted(df_separated.groups):
                local_idx = df_separated.groups[local_gr]

                local_df = self.df.ix[local_idx]

                # sets-up title
                if not isinstance(local_gr, type((0,))):
                    local_gr = [local_gr]
                local_title = ", ".join([
                                            "$%s = %s$" % (self.get_transformed_var(k), v)
                                            for (k, v) in zip(self.separated_vars, local_gr)
                                            ])
                # print local_title,
                for curr_y_axis in self.y_axis:
                    # print curr_y_axis,
                    # creates figure
                    #curr_fig = plt.figure(figsize=FIGSIZE)
                    plt.clf()
                    # adds all curves
                    self.add_curves(local_df, curr_y_axis, plt.gca())
                    plt.legend()

                    # sets-up title
                    plt.title(local_title)

                    # sets-up axes
                    plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                    plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

                    curr_axes = plt.gca()
                    curr_axes.tick_params(labelsize=18)

                    if curr_y_axis in self.settings:
                        # print self.settings[curr_y_axis],
                        if 'lim' in self.settings[curr_y_axis]:
                            plt.ylim(self.settings[curr_y_axis]['lim'])
                        if 'scale' in self.settings[curr_y_axis]:
                            curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
                    if self.x_axis in self.settings:
                        if 'lim' in self.settings[self.x_axis]:
                            plt.xlim(self.settings[self.x_axis]['lim'])
                        if 'scale' in self.settings[self.x_axis]:
                            curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                plt.tight_layout()
                plt.savefig(pp, format='pdf')
                # print

        pp.close()

    def plot_errorbar_all(self, output_name):
        df_separated = self.df.groupby(self.separated_vars, sort = True)
        pp = mpl_b_pdf.PdfPages( output_name )

        for local_gr in  sorted( df_separated.groups):
            local_idx = df_separated.groups[local_gr]

            local_df = self.df.ix[ local_idx ]

            # sets-up title
            if not isinstance(local_gr, type((0,))):
                local_gr = [local_gr]
            local_title = ", ".join( [ "$%s = %s$"%(self.get_transformed_var(k),v)
                                         for (k,v) in zip(self.separated_vars,
                                        local_gr)
                                        ])
            # print local_title,
            for curr_y_axis in self.y_axis:
                # print curr_y_axis,
                # creates figure
                plt.clf()
                #curr_fig = plt.figure(figsize=FIGSIZE)
                # adds all curves
                self.add_curves(local_df, local_gr, curr_y_axis, plt.gca())
                plt.legend()

                # sets-up title
                plt.title(local_title)

                # sets-up axes

                plt.xlabel(self.get_transformed_var(self.x_axis, keep_tex=True))


                plt.ylabel(self.get_transformed_var(curr_y_axis, keep_tex=True))

                curr_axes = plt.gca()
                curr_axes.tick_params(labelsize=18)

                if curr_y_axis in self.settings:
                    #print self.settings
                    if 'lim' in self.settings[curr_y_axis]:
                        plt.ylim(self.settings[curr_y_axis]['lim'])
                    if 'scale' in self.settings[curr_y_axis]:
                        curr_axes.set_yscale(self.settings[self.y_axis]['scale'])
                if self.x_axis in self.settings:
                    print(self.settings[self.x_axis])
                    if 'lim' in self.settings[self.x_axis]:
                        plt.xlim(self.settings[self.x_axis]['lim'])
                    if 'scale' in self.settings[self.x_axis]:
                        curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                plt.savefig(pp, format='pdf')
                # print

        pp.close()


class SPGBaseSubPlotter(SPGBasePlotter):
    def plot_all(self, output_name):
        if len(self.separated_vars) == 0:
            df_separated = self.df
        else:
            df_separated = self.df.groupby(self.separated_vars, sort=True)
        pp = mpl_b_pdf.PdfPages(output_name)

        for local_gr in sorted(df_separated.groups):

            local_idx = df_separated.groups[local_gr]
            local_df = self.df.ix[local_idx]

            # sets-up title
            if not isinstance(local_gr, type((0,))):
                local_gr = [local_gr]

            local_title = ", ".join([
                                        "$%s = %s$" % (self.get_transformed_var(k), v)
                                        for (k, v) in zip(self.separated_vars, local_gr)
                                        ])

            for curr_page in self.y_axis:
                print(local_title, curr_page)
                curr_fig, all_subp = plt.subplots(len(curr_page), sharex=True)

                for irow, curr_y_axis in enumerate(curr_page):
                    subp = all_subp[irow]
                    # creates figure
                    # curr_fig = plt.subplot(len(curr_page), 1, irow+1, sharex = True)
                    # adds all curves
                    self.add_curves(local_df, local_gr, curr_y_axis, subp)

                    if irow == 0:
                        subp.legend()
                        # sets-up title
                        subp.set_title(local_title)

                        # sets-up axes
                    if irow == len(curr_page) - 1:
                        subp.set_xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                    subp.set_ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

                    subp.tick_params(labelsize=18)

                    if curr_y_axis in self.settings:
                        if 'lim' in self.settings[curr_y_axis]:
                            subp.set_ylim(self.settings[curr_y_axis]['lim'])
                        if 'scale' in self.settings[curr_y_axis]:
                            subp.set_yscale(self.settings[self.y_axis]['scale'])
                    if self.x_axis in self.settings:
                        if 'lim' in self.settings[self.x_axis]:
                            subp.set_xlim(self.settings[self.x_axis]['lim'])
                        if 'scale' in self.settings[self.x_axis]:
                            subp.set_xscale(self.settings[self.x_axis]['scale'])

                curr_fig.subplots_adjust(hspace=0)
                plt.savefig(pp, format='pdf')

        pp.close()


class SPGAbstractPlotter:
    colors = ['black', 'blue', 'green', 'red', 'yellow', 'brown', 'grey', 'violet']
    markers = mlines.Line2D.filled_markers


    def __init__(self, table_name):
        init_mpl()

        self.df = pd.read_csv(table_name)

        self.column_names = self.df.columns  # column_names

    def get_transformed_var(self, var):
        if isinstance(var, type((0,))):
            var, foo = var
        if var in self.settings and "label" in self.settings[var]:
            #     print self.settings[var]["label"].replace("$","").replace("\\\\",'\\')
            return self.settings[var]["label"].replace("$", "").replace("\\\\", '\\')
        else:
            return var.replace("$", "").replace("_", "\_")

    def add_curves(self, local_df, curr_y_axis, subp, legend_prepend=""):

        df_coalesced = local_df.groupby(self.coalesced_vars)

        color_it = itertools.cycle(self.colors)
        marker_it = itertools.cycle(self.markers)
        for minimal_gr in sorted(df_coalesced.groups):

            minimal_idx = df_coalesced.groups[minimal_gr]

            minimal_df = self.df.ix[minimal_idx]

            if not isinstance(minimal_gr, type((0,))):
                minimal_gr = [minimal_gr]
            minimal_legend = legend_prepend + ", ".join([
                                                            "$%s = %s$" % (self.get_transformed_var(k), v)
                                                            for (k, v) in zip(self.coalesced_vars, minimal_gr)
                                                            ])
            #            print local_legend,  "------>",minimal_legend
            if isinstance(curr_y_axis, type("")):
                subp.scatter(minimal_df[[self.x_axis]], minimal_df[[curr_y_axis]],
                             label=minimal_legend, marker=next(marker_it), color=next(color_it), edgecolors="black",
                             s=65)
            elif isinstance(curr_y_axis, type((0,))) and len(curr_y_axis) == 2:
                ## BROKEN
                curr_y_axis, curr_yerr = curr_y_axis
                ####### B
                # subp.errorbar( x=minimal_df[[self.x_axis]], y=minimal_df[[curr_y_axis]] ,yerr = minimal_df[[curr_yerr]],
                #           label = minimal_legend, fmt = marker_it.next(), color = color_it.next(), edgecolors = "black", s = 65 )
                subp.errorbar(x=minimal_df[[self.x_axis]].apply(np.float32),
                              y=minimal_df[[curr_y_axis]].apply(np.float32),
                              yerr=minimal_df[[curr_yerr]].apply(np.float32))

    def plot_all(self, output_name):
        pp = mpl_b_pdf.PdfPages(output_name)

        if len(self.separated_vars) == 0:
            df_separated = self.df

            for curr_y_axis in self.y_axis:
                print(curr_y_axis, end=' ')
                # creates figure
                plt.clf()
                #curr_fig = plt.figure(figsize=FIGSIZE)
                # adds all curves
                self.add_curves(df_separated, curr_y_axis, plt.gca())
                plt.legend()

                # sets-up title
                #        plt.title(local_title)

                # sets-up axes
                plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

                curr_axes = plt.gca()
                curr_axes.tick_params(labelsize=18)

                if curr_y_axis in self.settings:
                    # print self.settings[curr_y_axis],
                    if 'lim' in self.settings[curr_y_axis]:
                        plt.ylim(self.settings[curr_y_axis]['lim'])
                    if 'scale' in self.settings[curr_y_axis]:
                        curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
                if self.x_axis in self.settings:
                    if 'lim' in self.settings[self.x_axis]:
                        plt.xlim(self.settings[self.x_axis]['lim'])
                    if 'scale' in self.settings[self.x_axis]:
                        curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                plt.gca().tight_layout()
                plt.savefig(pp, format='pdf')




        else:
            df_separated = self.df.groupby(self.separated_vars, sort=True)

            for local_gr in sorted(df_separated.groups):
                local_idx = df_separated.groups[local_gr]

                local_df = self.df.ix[local_idx]

                # sets-up title
                if not isinstance(local_gr, type((0,))):
                    local_gr = [local_gr]
                local_title = ", ".join([
                                            "$%s = %s$" % (self.get_transformed_var(k), v)
                                            for (k, v) in zip(self.separated_vars, local_gr)
                                            ])
                print(local_title, end=' ')
                for curr_y_axis in self.y_axis:
                    print(curr_y_axis, end=' ')
                    # creates figure
                    plt.clf()
                    #curr_fig = plt.figure(figsize=FIGSIZE)
                    # adds all curves
                    self.add_curves(local_df, curr_y_axis, plt.gca(),
                                    legend_prepend=self.get_transformed_var(curr_y_axis))
                    plt.legend()

                    # sets-up title
                    plt.title(local_title)

                    # sets-up axes
                    plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                    plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

                    curr_axes = plt.gca()
                    curr_axes.tick_params(labelsize=18)

                    if curr_y_axis in self.settings:
                        # print self.settings[curr_y_axis],
                        if 'lim' in self.settings[curr_y_axis]:
                            plt.ylim(self.settings[curr_y_axis]['lim'])
                        if 'scale' in self.settings[curr_y_axis]:
                            curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
                    if self.x_axis in self.settings:
                        if 'lim' in self.settings[self.x_axis]:
                            plt.xlim(self.settings[self.x_axis]['lim'])
                        if 'scale' in self.settings[self.x_axis]:
                            curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                    plt.savefig(pp, format='pdf')
                    print()
                    plt.tight_layout()

        pp.close()

    def plot_all_join_outputs(self, output_name):
        pp = mpl_b_pdf.PdfPages(output_name)

        if len(self.separated_vars) == 0:
            df_separated = self.df

            for curr_y_axis in self.y_axis:
                print(curr_y_axis, end=' ')
                # creates figure
                #curr_fig = plt.figure(figsize=FIGSIZE)
                plt.clf()
                # adds all curves
                self.add_curves(df_separated, curr_y_axis, plt.gca())
                plt.legend()

                # sets-up title
                #        plt.title(local_title)

                # sets-up axes
                plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

            curr_axes = plt.gca()
            curr_axes.tick_params(labelsize=18)

            if curr_y_axis in self.settings:
                # print self.settings[curr_y_axis],
                if 'lim' in self.settings[curr_y_axis]:
                    plt.ylim(self.settings[curr_y_axis]['lim'])
                if 'scale' in self.settings[curr_y_axis]:
                    curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
            if self.x_axis in self.settings:
                if 'lim' in self.settings[self.x_axis]:
                    plt.xlim(self.settings[self.x_axis]['lim'])
                if 'scale' in self.settings[self.x_axis]:
                    curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
            plt.gca().tight_layout()
            plt.savefig(pp, format='pdf')




        else:
            df_separated = self.df.groupby(self.separated_vars, sort=True)

            for local_gr in sorted(df_separated.groups):
                local_idx = df_separated.groups[local_gr]

                local_df = self.df.ix[local_idx]

                # sets-up title
                if not isinstance(local_gr, type((0,))):
                    local_gr = [local_gr]
                local_title = ", ".join([
                                            "$%s = %s$" % (self.get_transformed_var(k), v)
                                            for (k, v) in zip(self.separated_vars, local_gr)
                                            ])
                print(local_title, end=' ')
                for curr_y_axis in self.y_axis:
                    print(curr_y_axis, end=' ')
                    # creates figure
                    #curr_fig = plt.figure(figsize=FIGSIZE)
                    plt.clf()
                    # adds all curves
                    self.add_curves(local_df, curr_y_axis, plt.gca())
                    plt.legend()

                    # sets-up title
                    plt.title(local_title)

                    # sets-up axes
                    plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                    plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

                    curr_axes = plt.gca()
                    curr_axes.tick_params(labelsize=18)

                    if curr_y_axis in self.settings:
                        # print self.settings[curr_y_axis],
                        if 'lim' in self.settings[curr_y_axis]:
                            plt.ylim(self.settings[curr_y_axis]['lim'])
                        if 'scale' in self.settings[curr_y_axis]:
                            curr_axes.set_yscale(self.settings[curr_y_axis]['scale'])
                    if self.x_axis in self.settings:
                        if 'lim' in self.settings[self.x_axis]:
                            plt.xlim(self.settings[self.x_axis]['lim'])
                        if 'scale' in self.settings[self.x_axis]:
                            curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                plt.tight_layout()
                plt.savefig(pp, format='pdf')
                print()

        pp.close()

    def plot_errorbar_all(self, output_name):
        df_separated = self.df.groupby(self.separated_vars, sort=True)
        pp = mpl_b_pdf.PdfPages(output_name)

        for local_gr in sorted(df_separated.groups):
            local_idx = df_separated.groups[local_gr]

            local_df = self.df.ix[local_idx]

            # sets-up title
            if not isinstance(local_gr, type((0,))):
                local_gr = [local_gr]
            local_title = ", ".join([
                                        "$%s = %s$" % (self.get_transformed_var(k), v)
                                        for (k, v) in zip(self.separated_vars, local_gr)
                                        ])
            print(local_title, end=' ')
            for curr_y_axis in self.y_axis:
                print(curr_y_axis, end=' ')
                # creates figure
                #curr_fig = plt.figure(figsize=FIGSIZE)
                plt.clf()
                # adds all curves
                self.add_curves(local_df, local_gr, curr_y_axis, plt.gca())
                plt.legend()

                # sets-up title
                plt.title(local_title)

                # sets-up axes
                plt.xlabel("$%s$" % self.get_transformed_var(self.x_axis))

                plt.ylabel("$%s$" % self.get_transformed_var(curr_y_axis))

                curr_axes = plt.gca()
                curr_axes.tick_params(labelsize=18)

                if curr_y_axis in self.settings:
                    print(self.settings)
                    if 'lim' in self.settings[curr_y_axis]:
                        plt.ylim(self.settings[curr_y_axis]['lim'])
                    if 'scale' in self.settings[curr_y_axis]:
                        curr_axes.set_yscale(self.settings[self.y_axis]['scale'])
                if self.x_axis in self.settings:
                    print(self.settings[self.x_axis])
                    if 'lim' in self.settings[self.x_axis]:
                        plt.xlim(self.settings[self.x_axis]['lim'])
                    if 'scale' in self.settings[self.x_axis]:
                        curr_axes.set_xscale(self.settings[self.x_axis]['scale'])
                plt.savefig(pp, format='pdf')
            print()

        pp.close()



