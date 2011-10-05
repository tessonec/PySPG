#!/usr/bin/python
'''
Created on Sep 21, 2011

@author: tessonec
'''


import spg.utils as utils 


import numpy as np
import igraph as ig
import math as m
import random as rnd
import optparse, sys, os





class ModelDecay:
    
    def __init__(self, sz):
        self.size = sz
        self.zeta = 1
        self.alpha = 0.5
        
        self.graph = ig.Graph(self.size, directed = False)
        
    def init_full(self):
        edges = []
        for i in range(self.size):
            for j in range(i+1,self.size):
                edges.add( (i,j) )
                
        self.graph.add_edges(edges)

    def init_half_full(self):
        edges = []
        for i in range(self.size):
            for j in range(i+1,self.size-i):
                edges.add( (i,j) )
                
        self.graph.add_edges(edges)

    def iterate(self):
        for i_try in range(self.size):
            coin = rnd.random()
            if coin < self.alpha:
                self.try_node_add()
            else:
                self.try_node_remove()
    
    
    def select_slot(self, n_list, probs):
        ac = probs[0] 
        val  = rnd.random()
        destination = n_list[0]
        i_pos = 0
#        print probs
        while ac < val:
            i_pos += 1
            ac += probs[i_pos]
            destination=n_list[i_pos]
            
        return destination
    
    def try_node_add(self):
#        print "adding"
        pos_node = rnd.randint(0,self.size-1)
        self.non_neighs = set(range(self.size)  ) - set( self.graph.get_adjlist()[pos_node] ) - set([pos_node]) 
        if not self.non_neighs: return 
        self.non_neighs = [ i for i in self.non_neighs ] 
#        print pos_node, len(self.non_neighs), self.non_neighs
        self.calculate_connection_probabilities_on_addition( pos_node )
#        print ">>>"
        destination = self.select_slot( self.non_neighs, self.connection_probabilities ) 
#        print "<<<"
        self.graph.add_edges( (pos_node, destination) )
  

    def try_node_remove(self):
 #       print "removing"
        pos_node = rnd.randint(0,self.size-1)
        self.neighs = set( self.graph.get_adjlist()[pos_node] )
        
        if not self.neighs: return 
        self.neighs = [ i for i in self.neighs ]

        self.calculate_connection_probabilities_on_removal( pos_node )
        
        destination = self.select_slot( self.neighs, self.connection_probabilities ) 
        eid = self.graph.get_eid( pos_node, destination)
        self.graph.delete_edges( eid )
  


    def calculate_connection_probabilities_on_addition( self, pos_node ):
        n_elems = len(self.non_neighs)
        self.connection_probabilities = np.zeros( n_elems )
        
        for i in range( n_elems ):
            result = self.calculate_ec_added_edge(pos_node, self.non_neighs[i] )
            self.connection_probabilities[i] = m.exp(result/self.zeta)
            
        self.connection_probabilities = self.connection_probabilities / np.sum( self.connection_probabilities )
    

    def calculate_connection_probabilities_on_removal( self, pos_node ):
        n_elems = len(self.neighs)
        self.connection_probabilities = np.zeros( n_elems )
        for i in range( len(self.neighs) ):
            result = self.calculate_ec_removed_edge(pos_node, self.neighs[i] )
            self.connection_probabilities[i] = m.exp(-result/self.zeta)
        self.connection_probabilities = self.connection_probabilities / np.sum( self.connection_probabilities )
 

    def calculate_ec_added_edge(self, pos_node,  target_node):
        self.graph.add_edges( (pos_node, target_node)  )
        ret = self.graph.eigenvector_centrality()[pos_node]
        eid = self.graph.get_eid( pos_node, target_node)
        self.graph.delete_edges( eid )
        return ret


    def calculate_ec_removed_edge(self, pos_node,  target_node):
        eid = self.graph.get_eid( pos_node, target_node)
        self.graph.delete_edges( eid )
        ret = self.graph.eigenvector_centrality()[pos_node]
        self.graph.add_edges( (pos_node, target_node)  )
        return ret






if __name__ == "__main__":
    

    
    parameters = utils.load_parameters(sys.argv)
    utils.newline_msg("INF", "parameters: %s"%parameters )

    if parameters['store_dynamics']:
        fout_dynamics = open(parameters['store_dynamics_filename'],"w")
    if parameters['store_adj_matrix']:
        fout_adj_matrix = open(parameters['store_adj_matrix_filename'],"w")
    
    
    size = parameters['size']
    net = ModelDecay( size )
    
    if parameters['initial_condition'] == "HALF":
        net.init_half_full()
    elif parameters['initial_condition'] == "FULL":
        net.init_full()
    
    net.alpha = parameters['alpha']
    net.zeta = parameters['zeta']
    
    for i_time in range( parameters['filter_time'] ):
        net.iterate()

    for i_time in range( parameters['simulation_time'] ):
        net.iterate()
        if parameters['store_dynamics']:
                degrees = net.graph.degree()

                print >> fout_dynamics,  i_time, 
                print >> fout_dynamics,  len( net.graph.get_edgelist() ), 
                print >> fout_dynamics,  net.graph.average_path_length(),
        
                print >> fout_dynamics,  max(degrees),  
                print >> fout_dynamics, 2.* np.sum( degrees ) / float(size)  / float(size-1),  
                print >> fout_dynamics, np.max( degrees ) 

    c1,c2 = get_centralisation( net.graph )
    
    degrees = net.graph.degree()
    print c1, c2,    
    print len( net.graph.get_edgelist() ), 
    print net.graph.average_path_length(),
        
    print max(degrees),  
    print 2.* np.sum( degrees ) / float(size)  / float(size-1)
    if parameters['store_adj_matrix']:
        m = net.grap.get_adjacency()
        for i in range(size):
            for j in range(size):
                print >> fout_adj_matrix,  m[i,j],
            print >> fout_adj_matrix
        
