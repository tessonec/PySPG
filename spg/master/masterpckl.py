from spg import  TIMEOUT, VAR_PATH

import pickle
import spg.utils as utils

from spg.parameter import ParameterEnsemble


class PickledMaster:

    def __init__(self, EnsembleConstructor = ParameterEnsemble):
            
        self.EnsembleConstructor = EnsembleConstructor
        
        self.result_dbs = {} 
        self.active_dbs = set()

        self.normalising = 0.
 
        self.current_id = 0

        #:::~ DBs status can be either 
        #:::~    'S': stopped
        #:::~    'R': running
        #:::~    'F': finished

        #:::~ Queues status can be either
        #:::~    'S': stopped
        #:::~    'R': running

    @classmethod    
    def from_pickle(cls, fin):
         obj = pickle.load( open(fin) ) 
         obj.file_name = fin
         
         return obj
    
    def add_db(self, full_name, d):
        assert d.has_key( "id" )
        assert d.has_key( "weight" )
        assert d.has_key( "status" )

        if d['status']== 'R':
           self.normalising += d['weight']
           self.active_dbs.add( self.result_dbs[ full_name ] )
        
        self.result_dbs[ full_name ] = d.copy()
        
    def remove_db(self, full_name):
         utils.newline_msg("MSG", "removing db '%s' from the running list"%full_name)
         
         if self.result_dbs[full_name]['status']== 'R':
             self.normalising -= self.result_dbs[full_name]['weight']
             self.active_dbs.remove( self.result_dbs[ full_name ] )
         del self.result_dbs[full_name]
    
    def dump(self):
        pickle.dump( self, self.file_name )
        
    def update(self,full_name, **kwd):
        assert self.results_db.has_key(full_name)
        if self.results_db[k]['status'] == "R" : # Prev_status: running
            self.normalising -= self.result_dbs[full_name]['weight']
            self.active_dbs.remove( self.result_dbs[ full_name ] )
            
        for k in kwd:
            self.results_db[k] = kwd[k]
        
        if kwd['status']== 'R':
            self.normalising += d['weight']
            self.active_dbs.add( self.result_dbs[ full_name ] )
        
        