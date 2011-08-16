# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 08:10:30 2011

@author: -
"""

###################################################################################################


from spg import utils
from spg import VAR_PATH, TIMEOUT
from spg.parameter import ParameterAtom, ParameterEnsemble

from masterdb import MasterDB

import os
import random
import sqlite3 as sql





class DataExchanger(MasterDB):
#    waiting_processes = 100
    
    def __init__(self, connection = None):
        MasterDB.__init__(self, connection)
#        if master_connection:
#            self.connection = master_connection
#        else:
#            self.connection = sql.connect("%s/spg_pool.sqlite"%VAR_PATH, timeout = TIMEOUT)
#            
#        self.cursor = self.connection.cursor()
#        
#        self.dbs = {} 
#        self.update_dbs()
        
        self.current_counter = 0
        res = self.cursor.execute("SELECT last FROM infiles WHERE id = 1").fetchone()
        if res == None:
            self.cursor.execute("INSERT INTO infiles  (last) VALUES (0)")
            self.connection.commit()
#  print res
        
#        self.update_process_list()
#
#    def update_dbs(self): # These are the dbs that are registered and running
#        #self.dbs = {} 
#        ParameterEnsemble.normalising = 0.
#####         res = self.cursor.execute("SELECT id, full_name, weight, queue FROM dbs WHERE status = 'R'")
#        res = self.cursor.execute("SELECT id, full_name, weight, queue FROM dbs ")
#        vec = [(id, full_name, weight, queue) for (id, full_name, weight, queue) in res]
#    #    print self.dbs
#        toberemoved_dbs = set( self.dbs.keys() ) - set([full_name for (id, full_name, weight, queue) in vec])
#        for i in toberemoved_dbs:
#            self.dbs[i].close_db()
#            del self.dbs[i]
#    #    print self.dbs
#        
#        for (id, full_name, weight, queue) in vec:
#            if full_name in self.dbs.keys():
#                self.dbs[full_name].id = id
#                self.dbs[full_name].update_weight(weight)
#                self.dbs[full_name].queue = queue
##                print full_name, self.dbs[full_name].weight
#                continue
#            utils.newline_msg("INF","new db registered... '%s'"%full_name)
#            new_db = ParameterEnsemble(full_name, id, weight, queue)
#            self.dbs[full_name] = new_db
#    #    print self.dbs
#   


    def generate_new_process(self):
#     db_fits = False
#       print ParameterDB.normalising 
#      while not db_fits :
            rnd = ParameterEnsemble.normalising * random.random()
            ls_dbs = sorted( self.result_dbs.keys() )
            curr_db = ls_dbs.pop()
            ac = self.result_dbs[ curr_db ].weight
            
            while rnd > ac:
                curr_db = ls_dbs.pop()
                ac += self.result_dbs[ curr_db ].weight
            
#            res = self.dbs[ curr_db ].queue
#            if res == 'any' or res in res.split(","):
#               db_fits = True
#      print "CURR_DB",curr_db
            return  self.result_dbs[ curr_db ]


    def initialise_infiles(self):
        self.seeded_atoms =  self.waiting_processes - len(os.listdir("%s/queued"%(VAR_PATH) ) ) 
#      utils.newline_msg("INF", "initialise_infiles - %d"%to_run_processes )
#        print "inti"

        for i_atom in range(self.seeded_atoms):
            sel_db = self.generate_new_process(  )
#            utils.newline_msg("INF", "  >> %s/%s"%(sel_db.path,sel_db.db_name) )
        #    sel_db.next()
            
            (self.current_counter, ) = self.cursor.execute("SELECT last FROM infiles WHERE id = 1").fetchone()
            self.current_counter += 1
            self.cursor.execute("UPDATE infiles SET last = ? WHERE id = 1",(self.current_counter ,))
            self.db_master.commit()
            in_name = "in_%.10d"%self.current_counter
            pd = ParameterAtom(in_name, sel_db.full_name)
            ret = pd.load_next_from_ensemble( sel_db )
            if ret == None:
                continue
            pd.dump(src = "queued")



    def harvest_data(self):
        self.harvested_atoms  = len(os.listdir("%s/run"%(VAR_PATH) ))
        for i_d in os.listdir("%s/run"%(VAR_PATH) ):
            pd = ParameterAtom(i_d)
            pd.load(src = 'run')
            a_db =self.result_dbs[pd.full_db_name]
            pd.dump_result_in_ensemble( a_db  )

#
#    def synchronise_master(self):
#        for i in self.dbs:
#            icursor = self.dbs[i].cursor
#            icursor.execute("SELECT status, COUNT(*) FROM run_status GROUP BY status")
#            done, not_run, running,error = 0,0,0,0
#            for (k,v) in icursor:
#                if k == "D":
#                    done = v
#                elif k == "N":
#                    not_run = v
#                elif k == "R":
#                    running = v
#                elif k == "E":
#                    error = v
#            (no_combinations,) = icursor.execute("SELECT COUNT(*) FROM run_status ").fetchone()
#            (total_values_set,) = icursor.execute("SELECT COUNT(*) FROM values_set ").fetchone()
#
#            self.cursor.execute("UPDATE dbs SET total_values_set = ? , total_combinations = ?, done_combinations = ?, running_combinations = ?, error_combinations = ? WHERE full_name = ? ",(total_values_set, no_combinations, done, running, error,  self.dbs[i].full_name ))
#            if not_run == 0:
#                self.cursor.execute("UPDATE dbs SET status = ? WHERE full_name = ? ",('D',self.dbs[i].full_name))
#
#        self.connection.commit()

