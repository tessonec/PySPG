#!/usr/bin/python


import random as rnd
import threading, time
import spg.utils as utils


from spg.master import SPGMasterDB
from spg.simulation import ParameterEnsembleExecutor, ParameterEnsembleThreaded

class SPGRunningAtom(threading.Thread):
    n_threads = 0
    def __init__(self, ensemble, lock ):

        SPGRunningAtom.n_threads += 1
        threading.Thread.__init__(self)
        self.thread_id = SPGRunningAtom.n_threads

        self.ensemble = ensemble
        self.lock = lock

    def run(self):
        self.lock.acquire()
        print "-S- [%4d]- ----- %s" % (self.thread_id, self.ensemble.full_name)
        self.ensemble.next()
        self.lock.release()

        current_run_id, output, stderr, run_time = self.ensemble.launch_process()


        self.lock.acquire()
#        print "-X- [%4d]- ----- %s" % (self.thread_id, self.ensemble.full_name)
        self.ensemble.dump_result( current_run_id, output, stderr, run_time  )
#        self.ensemble.set_as_run()
        print "-X- [%4d]- ----- %s" % (self.thread_id, self.ensemble.full_name)
        self.lock.release()








class SPGRunningPool():
    def __init__(self):
        self.master_db = SPGMasterDB( EnsembleConstructor = ParameterEnsembleThreaded )
        self.lock = threading.Lock()
        # self.db_locks = {}

    def get_lock(self, i_db):
        if not self.db_locks.has_key( i_db.full_name ):
            self.db_locks[ i_db.full_name  ] = threading.Lock()
        return self.db_locks[ i_db.full_name  ]

    def launch_workers(self):
        target_jobs, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')

        current_count = self.active_threads()
        to_launch = target_jobs - current_count
        utils.newline_msg( "STAT", "[target:run/new]=[%d:%d/%d]" % (target_jobs,current_count, to_launch ) )


        self.master_db.update_list_ensemble_dbs()
        for i_t in range(to_launch):
            self.lock.acquire()
            pick = self.master_db.pick_ensemble()
            self.lock.release()

            nt = SPGRunningAtom(pick, self.lock)
            # nt = SPGRunningAtom(pick, lock=self.get_lock( pick ) )

            nt.start()

    def active_threads(self):
        return threading.active_count() - 1











#rp = SPGRunningPool(50, 2)
#rp.run()