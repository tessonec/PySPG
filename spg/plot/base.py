'''
Created on Aug 29, 2011

@author: tessonec
'''



class Curve:
    def __init__(self, values):
        self.values = values.copy()
        self.style = ""
        self.curve    

        
    
class Panel:
    def __init__(self, values, CurveConstructor = Curve):
        self.values = values.copy()
        self.curves = {}

        self.Curve = CurveConstructor


class Figure:
    def __init__(self, values, PanelConstructor = Panel, CurveConstructor = Curve):
        self.values = values.copy()
        self.panels = {}
        self.orientation = ""
        self.geometry = ""
        self.Panel = PanelConstructor
        self.Curve = CurveConstructor
        
    def add_panel(self, values):
        self.panels[ values ] = 
        
        
    def get_panel(self, values):
    
#        
#
#class PlotUnit:
#    def __init__(self, plot_object = None):
#        self.plot_object = plot_object
#        
#        self.x_label = ""
#        self.y_label = ""
#        
#        self.x_scale = "linear"
#        self.y_scale = "linear"
#        
#        self.x_range = None
#        self.y_range = None
#
#        self.autoscale = None
#        
#        self.curves = {}
#
#    def add_curve(self, curve_name, curve_object = None):
#        self.curves[curve_name] = curve_object
#
#    def refresh_style(self):
#        pass
#
#
#class GraphicsUnit:
#    def __init__(self, n_rows, n_plots):
#        (self.n_cols, self.n_rows) = self.get_geometry(n_rows, n_plots)
##        (self.n_cols, self.n_rows) = geometry
#        
#        self.subplots =  {}
#        
#    def add_subplot(self, subplot_name,  plot_unit = None):
#        self.subplots[subplot_name] = plot_unit
#    
#    def get_geometry(self, n_rows, n_plots):
#        if n_plots <= n_rows:
#            return ( 1,n_plots )
#        
#        n_cols = n_plots/float(n_rows)
#        n_cols = (int(n_cols) +1) if (n_cols - int(n_cols) > 0. ) else int(n_cols) 
#        return (n_cols,n_rows)

    