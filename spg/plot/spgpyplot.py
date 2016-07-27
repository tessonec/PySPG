import numpy as np
import math as m
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.pylab as plb

from spg.plot import GraphicsUnit, PlotUnit


class PyplotUnit(PlotUnit):
    __markers_progression = ['o', "s" ,"v", "D", "^", "<", ">", "p", "*", "p", "h", "H", "p"]
    __colours_progression = ['black', "blue", "green", "red", "yellow", "cyan", "white", "magenta", "navy", "violet"]
    __current_style = 0

    def __init__(self, plot_object = None):
        PlotUnit.__init__(self, plot_object)

    def __next_style(self):
        self.marker = self.__markers_progression[ self.__current_style % len( self.__markers_progression ) ]
        self.colour = self.__colours_progression[ self.__current_style % len( self.__colours_progression ) ]
        
        self.__current_style += 1 
    
    def add_curve(self, curve_name, datax, datay):
        
        obj, = self.plot_object.plot( datax, datay  )
        
        PlotUnit.add_curve(self, curve_name, curve_object = obj)
        self.__next_style()
        obj.set_marker(self.marker)
        obj.set_markerfacecolor(self.colour)
        obj.set_markeredgecolor("black")
        obj.set_linestyle("None")        


    def refresh_style(self):
        
        self.plot_object.set_xlabel( self.x_label) 
        self.plot_object.set_ylabel( self.y_label) 
#        print self.x_scale, self.y_scale
        self.plot_object.set_xscale(self.x_scale)
        self.plot_object.set_yscale(self.y_scale)
        x_min, x_max = self.x_range
        y_min, y_max = self.y_range
        if x_min and x_max:
            self.plot_object.set_xlim(self.x_range)
        if y_min and y_max:
            self.plot_object.set_ylim(self.y_range)
#        self.x_range = None
#        self.y_range = None
        self.plot_object.set_autoscale_on(self.autoscale)
            
       
        
class PyplotGraphicsUnit(GraphicsUnit):


    def __init__(self, fig_label, n_rows, n_plots):
        GraphicsUnit.__init__(self,n_rows, n_plots)
        self.label = fig_label
    #    print self.n_cols, self.n_rows, self.label
        rc('text', usetex=True)
        rc('font', family='serif')
        self.figure = plt.figure()
#        self.figure.set_title(r"$%s$"%self.label)
        
    def add_subplot(self, subplot_name):
        pos = 1 + len(self.subplots )
        print subplot_name, self.n_rows,  self.n_cols,pos
        obj = self.figure.add_subplot(self.n_rows,  self.n_cols, pos)
        
        GraphicsUnit.add_subplot( self, subplot_name, plot_unit = PyplotUnit( plot_object = obj ) )

#        
#pp = PyplotGraphicsUnit((3,2))
#pp.add_subplot("saf")
#pp.add_subplot("otro")
#pp.add_subplot("other")
#pp.add_subplot("foo")
#pp.add_subplot("mas")
#pp.add_subplot("fin")
##
#x = np.arange(0,10,.01)
#y1 = np.sin(x**2)
#y2 = np.sin(x**3)
#y3 = np.sin(x**4)
##
#print pp.subplots
##
#pp.subplots["saf"].add_curve( "**2", x, y1)
#pp.subplots["saf"].add_curve( "**3", x, y2)
#pp.subplots["foo"].add_curve( "**4", x, y3)
#pp.subplots["foo"].refresh_style()
#
#pp.subplots["mas"].add_curve( "**1", x, x)
#pp.subplots["mas"].refresh_style()
##
#plt.show()



#ax = plt.subplot(111)
#
#line1, = plt.plot(x, y1, lw=2)
#line2, = plt.plot(x, y2, lw=2)

#plt.ylim(-2,2)

#plt.show()
