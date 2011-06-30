# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 08:10:30 2011

@author: -
"""

###################################################################################################


from spg import utils, params
from parameter import ParameterDB
from data import AtomData


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
        self.update_dbs()
        
        self.current_counter = 0
        res = self.cur_master.execute("SELECT last FROM infiles WHERE id = 1").fetchone()
        if res == None:
           self.cur_master.execute("INSERT INTO infiles  (last) VALUES (0)")
           self.db_master.commit()
      #  print res
        
#        self.update_process_list()

    def update_dbs(self): # These are the dbs that are registered and running
        #self.dbs = {} 
        ParameterDB.normalising = 0.
        res = self.cur_master.execute("SELECT id, full_name, weight, queue FROM dbs WHERE status = 'R'")
        vec = [(id, full_name, weight, queue) for (id, full_name, weight, queue) in res]
        print self.dbs
        toberemoved_dbs = set( self.dbs.keys() ) - set([full_name for (id, full_name, weight, queue) in vec])
        for i in toberemoved_dbs:
          self.dbs[i].close_db()
          del self.dbs[i]
          
        for (id, full_name, weight, queue) in toberemoved_dbs:
            if full_name in self.dbs.keys():
                self.dbs[full_name].id = id
                self.dbs[full_name].weight = weight
                self.dbs[full_name].queue = queue
                
                continue
            utils.newline_msg("INF","new db registered... '%s'"%full_name)
            new_db = ParameterDB(full_name, id, weight, queue)
            self.dbs[full_name] = new_db
   


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
  #      print "CURR_DB",curr_db
        return  self.dbs[ curr_db ]


    def initialise_infiles(self):
        to_run_processes =  self.waiting_processes - len(os.listdir("%s/queued"%(VAR_PATH) ) ) 
  #      utils.newline_msg("INF", "initialise_infiles - %d"%to_run_processes )

        for i in range(to_run_processes):
            sel_db = self.generate_new_process(  )
       #     utils.newline_msg("INF", "  >> %s"%sel_db.db_name )
        #    sel_db.next()
            
            (self.current_counter, ) = self.cur_master.execute("SELECT last FROM infiles WHERE id = 1").fetchone()
            self.current_counter += 1
            self.cur_master.execute("UPDATE infiles SET last = ? WHERE id = 1",(self.current_counter ,))
            self.db_master.commit()
            in_name = "in_%.10d"%self.current_counter
            pd = AtomData(in_name, sel_db.full_name)
            ret = pd.load_next_from_db( sel_db.connection, sel_db.cursor )
            if ret == None:
                continue
            pd.dump(src = "queued")



    def harvest_data(self):
        self.last_finished_processes  = 0
        for i_d in os.listdir("%s/run"%(VAR_PATH) ):
            pd = AtomData(i_d)
            pd.load(src = 'run')
            a_db =self.dbs[pd.full_db_name]
            pd.dump_in_db( a_db.connection, a_db.cursor  )


    def synchronise_master(self):
        for i in self.dbs:
            icursor = self.dbs[i].cursor
            icursor.execute("SELECT status, COUNT(*) FROM run_status GROUP BY status")
            done, not_run, running,error = 0,0,0,0
            for (k,v) in icursor:
                if k == "D":
                  done = v
                elif k == "N":
                  not_run = v
                elif k == "R":
                  running = v
                elif k == "E":
                  error = v
            (no_combinations,) = icursor.execute("SELECT COUNT(*) FROM run_status ").fetchone()
            (total_values_set,) = icursor.execute("SELECT COUNT(*) FROM values_set ").fetchone()

            self.cur_master.execute("UPDATE dbs SET total_values_set = ? , total_combinations = ?, done_combinations = ?, running_combinations = ?, error_combinations = ? WHERE full_name = ? ",(total_values_set, no_combinations, done, running, error,  self.dbs[i].full_name ))
            if not_run == 0:
                self.cur_master.execute("UPDATE dbs SET status = ? WHERE full_name = ? ",('D',self.dbs[i].full_name))

        self.db_master.commit()



