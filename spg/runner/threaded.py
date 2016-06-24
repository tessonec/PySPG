#!/usr/bin/python


import random as rnd
import threading, time
import spg.utils as utils


from spg.master import SPGMasterDB

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
        print "-S- [%4d]- ----- " % (self.thread_id, self.ensemble.full_name)
        self.lock.release()

        time.sleep( rnd.randint( 2, 15 ) )

        self.lock.acquire()
        print "-X- [%4d]- ----- " % (self.thread_id, self.ensemble.full_name)
        self.lock.release()






class SPGRunningPool():
    def __init__(self):
        self.master_db = SPGMasterDB()

        self.db_lock = threading.Lock()



    def launch_workers(self):
        target_jobs, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')

        current_count = self.active_threads()
        to_launch = target_jobs - current_count
        utils.newline_msg( "STAT", "[%3d::%3d:%3d]" % (target_jobs,current_count, to_launch ) )


        self.master_db.update_list_ensemble_dbs()
        for i_t in range(to_launch):

            pick = self.master_db.pick_ensemble()

            nt = SPGRunningAtom(pick, lock=self.db_lock)
            nt.start()

    def active_threads(self):
        return threading.active_count() - 1











#rp = SPGRunningPool(50, 2)
#rp.run()