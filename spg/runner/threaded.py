#!/usr/bin/env python3



import random as rnd
import threading, time
import spg.utils as utils


from spg.master import SPGMasterDB
from spg.simulation import ParameterEnsembleExecutor, ParameterEnsembleThreaded


from collections import defaultdict
import math as m

class SPGRunningAtom(threading.Thread):
    n_threads = 0
    def __init__(self, ensemble, lock, active_processes ):

        SPGRunningAtom.n_threads += 1
        threading.Thread.__init__(self)
        self.thread_id = SPGRunningAtom.n_threads
        self.ensemble = ensemble
        self.lock = lock
        self.active_processes = active_processes


    def run(self):
        self.lock.acquire()
        next(self.ensemble)

        current_uid, current_vsid, current_rep, values = self.ensemble.get_current_information()
        print(utils.str_color("@green-S-@reset [%4d]- ----- %s / %d" % (self.thread_id, self.ensemble.full_name, current_uid) ))
        #print "-S- [%4d]- ----- %s / %d" % (self.thread_id, self.ensemble.full_name, current_run_id)
        self.lock.release()

        self.active_processes[ self.ensemble.full_name ] += 1

        current_uid, current_vsid, current_rep, output, stderr, run_time , return_code  = self.ensemble.launch_process(current_uid, current_vsid,current_rep, values)

        self.lock.acquire()
        self.ensemble.dump_result(current_uid, current_vsid, current_rep, output, stderr, run_time, return_code)
        if return_code == 0:
            self.ensemble.query_set_run_status("D", current_uid, run_time)
        elif return_code == -2:
            self.ensemble.query_set_run_status("N", current_uid, run_time)
        else:
            self.ensemble.query_set_run_status("E", current_uid, run_time)
        if return_code == 0:
            print(utils.str_color( "@cyan-X-@reset [%4d]- ----- %s / %d @cyan[%d]" % (self.thread_id, self.ensemble.full_name, current_uid, return_code) ))
        else:
            print(utils.str_color(
                "@red-X-@reset [%4d]- ----- %s / %d @red[%d]" % (self.thread_id, self.ensemble.full_name, current_uid, return_code)))
        self.active_processes[ self.ensemble.full_name ] -= 1
        self.lock.release()








class SPGRunningPool():
    def __init__(self, test_run = False):
        self.master_db = SPGMasterDB( EnsembleConstructor = ParameterEnsembleThreaded )
        self.test_run = test_run

        self.lock = threading.Lock()
        self.db_locks = {}
        ### :::~ The number of processes that are active in each spg file
        self.active_processes = defaultdict(lambda : 0)

    def get_lock(self, i_db):
        if i_db.full_name not in self.db_locks:
            self.db_locks[ i_db.full_name ] = threading.Lock()
        return self.db_locks[ i_db.full_name ]

    def launch_workers(self):
        target_jobs, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')

        self.master_db.update_list_ensemble_dbs()
        if len(self.master_db.active_dbs) == 0:
            utils.inline_msg("MSG", "No active dbs... sleeping ")
            return

        current_count = self.active_threads()
#        print "+++++++++++", to_launch
        vec_to_launch = []

        launch = defaultdict(lambda: 0)
        running = {}

        for ae in self.master_db.active_dbs:
            ens = self.master_db.result_dbs[ae  ]
            running[ ens['id'] ] = self.active_processes[ ae ]
            qty_to_launch = int( m.floor(0.5 + target_jobs*ens['weight']/self.master_db.normalising) - self.active_processes[ ae ] )

            vec_to_launch += qty_to_launch * [ae]
            launch[ ens['id'] ] += qty_to_launch
 #       for id in launch:
 #           print "+++ (%d) %d + %d = //%d//, "%( id, launch[id], running[id],launch[id]+running[id] )
 #       print

        to_launch = len(vec_to_launch)
        if to_launch >= 0:
             utils.newline_msg("STATUS", utils.str_color( "@green[n_jobs=%d] run=%d %s ::: new=%d" % (target_jobs,current_count, dict(running),to_launch) ) )
        else:
             utils.newline_msg("STATUS", utils.str_color( "@yellow[n_jobs=%d] run=%d :!: exceeded number" % (target_jobs,current_count)) )

 #       print to_launch, len( vec_to_launch ), launch

#        for i_t in range(to_launch):
        for ae in vec_to_launch:
            pick = self.master_db.EnsembleConstructor(ae, init_db=True)
            self.lock.acquire()
#            pick = self.master_db.pick_ensemble()

            pick.test_run = self.test_run

            status = pick.get_updated_status()
            if status['process_not_run'] == 0:
                print("+D+ ----- %s " % (pick.full_name))
                self.master_db.query_master_db('UPDATE dbs SET status= ? WHERE full_name = ?', "D", pick.full_name)
                return

            self.lock.release()

            nt = SPGRunningAtom(pick, self.lock, self.active_processes)
#            nt.test_run = self.test_run
            # nt = SPGRunningAtom(pick, lock=self.get_lock( pick ) )

            nt.start()

    def active_threads(self):
        return threading.active_count() - 1











#rp = SPGRunningPool(50, 2)
#rp.run()