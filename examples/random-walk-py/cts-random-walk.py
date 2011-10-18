#!/usr/bin/python
'''
Created on Sep 21, 2011

@author: tessonec
'''


import spg.utils as utils 


import math as m
import random as rnd
import sys





class ModelRandomWalk:
    
    def __init__(self):
        self.X = 0
        self.S = 0
        self.D = 1
        self.drift = 1
        

    def iterate(self):
        pos_change = rnd.normalvariate(0, self.D) +  self.drift ; 
        self.X +=pos_change
        self.S += pos_change*pos_change 






if __name__ == "__main__":
    

    
    parameters = utils.load_parameters(sys.argv)
    utils.newline_msg("INF", "parameters: \n %s" % parameters )

    
    
    system = ModelRandomWalk(  )
    system.D = parameters.D
    system.drift = parameters.drift
    
    
    for i_iter in range(parameters.simulation_timesteps):
      system.iterate()

    print system.X, system.S
