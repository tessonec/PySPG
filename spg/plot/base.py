'''
Created on Aug 29, 2011

@author: tessonec
'''

        

class PlotUnit:
    def __init__(self, plot_object = None):
        self.plot_object = plot_object
        
        self.x_label = ""
        self.y_label = ""
        
        self.x_scale = "linear"
        self.y_scale = "linear"
        
        self.x_range = None
        self.y_range = None

        self.autoscale = None
        
        self.curves = {}

    def add_curve(self, curve_name, curve_object = None):
        self.curves[curve_name] = curve_object

    def refresh_style(self):
        pass


class GraphicsUnit:
    def __init__(self, geometry = None):
        if geometry:
            (self.n_cols, self.n_rows) = geometry
            
        self.subplots =  {}
        
    def add_subplot(self, subplot_name,  plot_unit = None):
        self.subplots[subplot_name] = plot_unit
    
    
    