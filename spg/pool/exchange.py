# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 08:10:30 2011

@author: -
"""

###################################################################################################


from spg import utils, params
from parameter import ParameterDB
from data import PickledData


import os.path
import random
import sqlite3 as sql

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")
TIMEOUT = 120



class DataExchanger:
    waiting_processes = 100
    
    def __init__(self, db_master, cur_master):
        self.db_master = db_master
        self.cur_master = cur_master
        
        self.dbs = {} 
        self.get_registered_dbs()
        self.current_counter = 0
#        self.update_process_list()

    def get_registered_dbs(self): # These are the dbs that are registered and running
        self.dbs = {} 
        ParameterDB.normalising = 0.
        res = self.cur_master.execute("SELECT id, full_name, path, db_name, weight, queue FROM dbs WHERE status = 'R'")
        for (id, full_name, path, db_name, weight, queue) in res:
            self.dbs[full_name] = ParameterDB(full_name, path, db_name,id, weight, queue)


    def generate_new_process(self):
        db_fits = False
        while not db_fits :
            rnd = ParameterDB.normalising * random.random()
            ls_dbs = sorted( self.dbs.keys() )
            curr_db = ls_dbs.pop()
            ac = self.dbs[ curr_db ].weight
            
            while rnd > ac:
                curr_db = ls_dbs.pop()
                ac += self.dbs[ curr_db ].weight
            
            res = self.dbs[ curr_db ].queue
            if res == 'any' or res in res.split(","):
               db_fits = True
     
        return  self.dbs[ curr_db ]


    def initialise_infiles(self):
        to_run_processes =  self.waiting_processes - len(os.listdir("%s/queued"%(VAR_PATH) ) ) 
        utils.newline_msg("INF", "initialise_infiles - %d"%to_run_processes )

        for i in range(to_run_processes):
            sel_db = self.generate_new_process(  )
            utils.newline_msg("INF", "  >> %s"%sel_db.db_name )
            sel_db.next()
        
            self.current_counter += 1
            in_name = "in_%.10d"%self.current_counter
            pd = PickledData(in_name)
            pd.full_name = sel_db.full_name
            pd.load_next_from_db( )
            
            pd.dump(src = "queued")

    def harvest_data(self):
        self.last_finished_processes  = 0
        for i_d in os.listdir("%s/run"%(VAR_PATH) ):
            pd = PickledData(id)
            pd.load(src = 'run')
            pd.dump_in_db()
    





