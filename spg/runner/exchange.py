# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 08:10:30 2011

@author: -
"""

###################################################################################################


from spg import utils
from spg import ROOT_DIR
from spg.simulation import ParameterAtom, ParameterEnsemble

from spg.master import SPGMasterDB #, PickledMaster


import os
import random

import fnmatch

#
# class MasterDBThreadedExchanger(SPGMasterDB):
#
#     def __init__(self, connection=None):
#         SPGMasterDB.__init__(self, connection)
#
#         self.normalising = 0.
#         self.active_dbs = []
#
#     def update_list_ensemble_dbs(self):
#
#         SPGMasterDB.update_list_ensemble_dbs(self)
#         self.normalising = 0.
#         self.active_dbs = []
#
#         for i in self.result_dbs.keys():
#             if self.result_dbs[i] is None:
#                 del self.result_dbs[i]
#                 utils.newline_msg("MSG", "removing db '%s' from the running list" % i)
#                 continue
#             if self.result_dbs[i].status == 'R':
#                 self.normalising += self.result_dbs[i].weight
#                 self.active_dbs.append(self.result_dbs[i])
#
#     def pick_ensemble(self):
#
#         rnd = self.normalising * random.random()
#
#         curr_db = self.active_dbs.pop()
#         ac = curr_db.weight
#
#         while rnd > ac:
#             curr_db = self.active_dbs.pop()
#             ac += curr_db.weight
#
#         return curr_db

    # def seed_atoms(self, queue_name):
    #     self.seeded_atoms = self.max_atoms_to_seed - len(os.listdir("%s/queue/%s" % (VAR_PATH, queue_name)))
    #     #      utils.newline_msg("INF", "initialise_infiles - %d"%to_run_processes )
    #     #        print "inti"
    #     self.update_ensemble_list()
    #     for i_atom in range(self.seeded_atoms):
    #         sel_db = self.pick_ensemble(queue_name)
    #         #            utils.newline_msg("INF", "  >> %s/%s"%(sel_db.path,sel_db.db_name) )
    #         #    sel_db.next()
    #
    #         (self.current_counter,) = self.execute_query_fetchone("SELECT last FROM infiles WHERE id = 1")
    #         self.current_counter += 1
    #         self.execute_query("UPDATE infiles SET last = ? WHERE id = 1", self.current_counter)
    #         #            self.db_master.commit()
    #         in_name = "in_%.10d" % self.current_counter
    #         pd = ParameterAtom(in_name, sel_db.full_name)
    #         ret = pd.load_next_from_ensemble(sel_db)
    #         if ret == None:
    #             continue
    #         pd.dump(src="queue/%s" % queue_name)
    #
    # def harvest_atoms(self):
    #     ls_atoms = os.listdir("%s/run" % (VAR_PATH))
    #     self.harvested_atoms = len(ls_atoms)
    #     for i_d in ls_atoms:
    #         pd = ParameterAtom(i_d)
    #         try:
    #             pd.load(src='run')
    #         except:
    #             utils.newline_msg("WRN", "could not pickle '%s'...skipping" % i_d, 2)
    #             os.system("rm -f %s/run/%s" % (VAR_PATH, i_d))
    #             continue
    #
    #         try:
    #             a_db = self.result_dbs[pd.full_db_name]
    #             pd.dump_result_in_ensemble(a_db)
    #         except KeyError:
    #             utils.newline_msg("SKP", "database '%s' not registered anymore, skipping" % pd.full_db_name, 2)
    #



















# :::~ COMMENTED OUT AS IT IS UNUSED WITHOUT QUEUES

# class MasterDBDataExchanger(SPGMasterDB):
#     max_atoms_to_seed = 100
#
#     def __init__(self, connection = None):
#         SPGMasterDB.__init__(self, connection)
#
#
#         self.current_counter = 0
#         res = self.cursor.execute("SELECT last FROM infiles WHERE id = 1").fetchone()
#         if res == None:
#             self.cursor.execute("INSERT INTO infiles  (last) VALUES (0)")
#             self.connection.commit()
#
#
#     def update_ensemble_list(self):
#             self.normalising = 0.
#             self.active_dbs = []
#        #     print "MasterDBDataExchanger::update_ensemble_list", self.result_dbs.keys()
#             for i in self.result_dbs.keys():
#        #         print "DE [---]",i, self.result_dbs[i], self.result_dbs[i].status
#                 if self.result_dbs[i] == None:
#                     del self.result_dbs[i]
#                     utils.newline_msg("MSG", "removing db '%s' from the running list"%i)
#                     continue
#                 if self.result_dbs[i].status == 'R':
#                     self.normalising += self.result_dbs[ i ].weight
#                     self.active_dbs.append( self.result_dbs[ i ] )
#
#
#
#     def pick_ensemble(self, queue_name):
#
#      #       print "MasterDBDataExchanger::pick_ensemble", queue_name, self.active_dbs
#             ls_dbs = [ i for i in self.active_dbs
#                        if fnmatch.fnmatch(queue_name, i.queue)
#                        ]
#       #      print queue_name, ls_dbs
#             self.normalising = 0
#             for i in ls_dbs:
#                 self.normalising += i.weight
#
#             rnd = self.normalising * random.random()
#
# #            ls_dbs = sorted( self.result_dbs.keys() )
#             curr_db = ls_dbs.pop()
#             ac =  curr_db.weight
#
#             while rnd > ac:
#                 curr_db = ls_dbs.pop()
#                 ac +=  curr_db.weight
#
#             return   curr_db
#
#
#     def seed_atoms(self, queue_name):
#         self.seeded_atoms =  self.max_atoms_to_seed - len(os.listdir("%s/queue/%s"%(ROOT_DIR,queue_name) ) )
# #      utils.newline_msg("INF", "initialise_infiles - %d"%to_run_processes )
# #        print "inti"
#         self.update_ensemble_list()
#         for i_atom in range(self.seeded_atoms):
#             sel_db = self.pick_ensemble( queue_name )
# #            utils.newline_msg("INF", "  >> %s/%s"%(sel_db.path,sel_db.db_name) )
#         #    sel_db.next()
#
#             (self.current_counter, ) = self.query_master_fetchone("SELECT last FROM infiles WHERE id = 1")
#             self.current_counter += 1
#             self.query_master_db("UPDATE infiles SET last = ? WHERE id = 1", self.current_counter)
# #            self.db_master.commit()
#             in_name = "in_%.10d"%self.current_counter
#             pd = ParameterAtom(in_name, sel_db.full_name)
#             ret = pd.load_next_from_ensemble( sel_db )
#             if ret == None:
#                 continue
#             pd.dump(src = "queue/%s"%queue_name)
#
#
#
#     def harvest_atoms(self):
#         ls_atoms = os.listdir("%s/run"%(ROOT_DIR) )
#         self.harvested_atoms  = len(ls_atoms)
#         for i_d in ls_atoms:
#             pd = ParameterAtom(i_d)
#             try:
#                 pd.load(src = 'run')
#             except:
#                 utils.newline_msg("WRN", "could not pickle '%s'...skipping"%i_d, 2)
#                 os.system("rm -f %s/run/%s"%(ROOT_DIR,i_d))
#                 continue
#
#             try:
#                 a_db =self.result_dbs[pd.full_db_name]
#                 pd.dump_result_in_ensemble( a_db  )
#             except KeyError:
#                 utils.newline_msg("SKP", "database '%s' not registered anymore, skipping"%pd.full_db_name,2)




#
#
# class PickledDataExchanger(PickledMaster):
#     max_atoms_to_seed = 100
#
#
#     def __init__(self, EnsembleConstructor = ParameterEnsemble):
#          PickledMaster.__init__(self, EnsembleConstructor)
#
#     def pick_ensemble(self):
#
#             rnd = self.normalising * random.random()
#             ls_dbs = [ i for i in self.active_dbs ]
#             if len( ls_dbs  ) == 0:
#                 return None
#
#             curr_db = ls_dbs.pop()
#             ac =  curr_db[ 'weight' ]
#
#             while rnd > ac:
#                 curr_db = ls_dbs.pop()
#                 ac +=  curr_db[ 'weight' ]
#
#             return  curr_db
#
#
#     def seed_atoms(self):
#         self.seeded_atoms =  self.max_atoms_to_seed - len(os.listdir("%s/queue/"%(VAR_PATH) ) )
#
#         self.update_ensemble_list()
#         for i_atom in range(self.seeded_atoms):
#             sel_db = self.pick_ensemble( )
#             self.current_counter += 1
#
#             in_name = "in_%.10d"%self.current_counter
#             pd = ParameterAtom(in_name, sel_db.full_name)
#             ret = pd.load_next_from_ensemble( sel_db )
#             if ret == None:
#                 continue
#             pd.dump(src = "queue")
#
#
#
#     def harvest_atoms(self):
#         ls_atoms = os.listdir("%s/run"%(VAR_PATH) )
#         self.harvested_atoms  = len(ls_atoms)
#         for i_d in ls_atoms:
#             pd = ParameterAtom(i_d)
#             try:
#                 pd.load(src = 'run')
#             except:
#                 utils.newline_msg("WRN", "could not pickle '%s'...skipping"%i_d, 2)
#                 os.system("rm -f %s/run/%s"%(VAR_PATH,i_d))
#                 continue
#
#             try:
#                 a_db =self.result_dbs[pd.full_db_name]
#                 pd.dump_result_in_ensemble( a_db  )
#             except KeyError:
#                 utils.newline_msg("SKP", "database '%s' not registered anymore, skipping"%pd.full_db_name,2)
