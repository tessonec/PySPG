import numpy as np
import math as m
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.pylab as plb


class PyplotStyle:
    
    markers_progression = ['o', "s" ,"v", "D", "^", "<", ">", "p", "*", "p", "h", "H", "p"]
    colours_progression = ['black', "blue", "green", "red", "yellow", "cyan", "white", "magenta", "navy", "violet"]
    
    current_pos = 0
    
    def __init__(self):
        self.next()


    def next(self):
        self.marker = self.markers_progression[ self.current_pos % len( self.markers_progression ) ]
        self.colour = self.colours_progression[ self.current_pos % len( self.colours_progression ) ]
        
        self.current_pos += 1 
        
    
#    def __init__(self):
#        rc('text', usetex=True)
#        rc('font', family='serif')
#        
#        self.figure_dict = {}
#
#        self.figure = plt.figure()
#        
#    
#    
#    
#    
#    
#    def show(self):
#        plt.show()
#        
#    
#    
#    
pw = PyplotWrapper() 
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
print pw.marker,pw.colour
pw.next()
